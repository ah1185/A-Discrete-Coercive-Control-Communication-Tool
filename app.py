from flask import Flask, render_template, request, redirect, session, jsonify
from flask_session import Session
from ConfigResolver import *
from UserResolver import UserResolver
from Analyser import Analyser
from EventListener import *
from flask_apscheduler import APScheduler
import requests
from base64 import b64encode
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash
from dash import dcc, html
from Dashboard import Dashboard
import bcrypt
import os
from PhoneNumberValidationFunction import isValidUKMobileNumber

app = Flask(__name__, 
            static_url_path='',
            static_folder='web/static',
            template_folder='templates')

app.config["SESSION_PERMANENT"] = False 
app.config["SESSION_TYPE"] = "filesystem" 
Session(app)
app.secret_key = os.environ.get("SECRET_KEY")
spotifyAppClientID = os.environ.get("SPOTIFY_APP_CLIENT_ID")
spotifyAppSecret = os.environ.get("SPOTIFY_APP_SECRET")
spotifyTriggerTrack = os.environ.get("SPOTIFY_TRIGGER_TRACK")#track used to trigger event
url = os.environ.get("SPOTIFY_URL") + spotifyTriggerTrack


dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/', external_stylesheets=[dbc.themes.BOOTSTRAP])

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

def spotifyAuthentication(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

def spotifyUsersPoll():
    """
    Poll Spotify API to monitor track status changes for all linked users.

    This function:
    1. Retrieves all Spotify-linked users from the database
    2. Handles token refresh when access tokens expire (401)
    3. Triggers events when the specified track's status has changed 

    Notes:
    - Spotify access tokens expire after 1 hour
    """
    userResolver = UserResolver()
    users = userResolver.getSpotifyLinkedUsers() 
    for user in users: 
        response = requests.get(url, headers={"Authorization":"Bearer " + user["spotifyAccessToken"]})
        if response.status_code == 401 : 
            newToken = requests.post('https://accounts.spotify.com/api/token', data = {'grant_type':'refresh_token','refresh_token':user["spotifyRefreshToken"], 'client_id' : spotifyAppClientID},headers={'Content-Type': 'application/x-www-form-urlencoded', 'Authorization' : spotifyAuthentication(spotifyAppClientID, spotifyAppSecret)})
            if newToken.status_code == 200:
                user["spotifyAccessToken"] = newToken.json()["access_token"] 
                result = userResolver.saveSpotifyAccessToken(str(user["_id"]),user["spotifyAccessToken"])
                if not result:
                    print("Error saving new access token to DB")         
                response = requests.get(url, headers={"Authorization":"Bearer " + user["spotifyAccessToken"]})
            else:
                user["spotifyAccessToken"] = None
                user["spotifyRefreshToken"] = None
        if response.status_code == 200 : 
            if response.json()[0] == user["spotifyTrackToggle"]:  # song status has changed
                #set to true/false, if it's the same, do nothing. first time you expect it to be false, they don't have it in library
                print("Song added / removed from library")
                # set toggle the opposite of what it is  so that next time you look t see if it has changed   
                user["spotifyTrackToggle"] = not user["spotifyTrackToggle"] 
                result = userResolver.saveSpotifyTrackToggle(str(user["_id"]),user["spotifyTrackToggle"])
                if not result:
                    print("Error saving track toggle to DB")    
                newEvent = SpotifyEventListener(str(user["_id"]))
                newEvent.sendData()
                
#starts spotify poll
scheduler.add_job(id='spotifyPoll', func=spotifyUsersPoll, trigger='interval', seconds=int(os.environ.get("SPOTIFY_POLL_INTERVAL"))) #call function spotify poll every x seconds



########################################################
#       Webpage Template Renderers
########################################################
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register')
def display_register():
    return render_template('register.html')

@app.route('/login')
def display_login():
    return render_template('login.html')

@app.route('/addActions')
def display_config():
    if not session.get("userid"):
        return redirect("/login")
    return render_template('config.html', active_page='config')

@app.route('/help')
def display_help():
    if not session.get("userid"):
        return redirect("/login")
    return render_template('help.html', active_page='help')

@app.route('/logout')
def display_logout():
    session["userid"] = None
    return redirect("/")

@app.route('/dashboard/')
def serve_dashboard():
    if not session.get('userid'):
        return redirect('/login')
    return dash_app.index()

########################################################
#       Website APIs
########################################################

@app.route('/register', methods=['POST'])
def register():
    """
    Registers a new user with email and password.

    Stores email and a bcrypt-hashed password, securely hashed with a randomly generated salt.
    Upon successful registration, the user is automatically logged in (session created).
    
    Expects a JSON payload with:
        email (str): User's email address 
        password (str): Plaintext password to be hashed and stored

    Returns:
        JSON response with either:
        - Success message and userID with HTTP 200 status on successful registration
        - Error message with HTTP 400 status if request is invalid

    """
    requestJSON = request.get_json()
    try:
        newResolver = UserResolver()
        if newResolver.getUserByEmail(requestJSON['email']) != None:
            return jsonify({
                'error': "User already exists"
            }), 400
        else:
            password = requestJSON['password'].encode('utf-8') 
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password, salt)
            print("Salt :",salt,"Hashed",hashed)
            userID = newResolver.saveUser(requestJSON['email'],hashed,"user")
            session["userid"] = userID
            return jsonify({
                'message': f"User registered: {userID}"
            }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 400


@app.route('/config', methods=['POST'])
def configUpdate():
    """
    Update user configuration via a POST request.

    Allows authenticated users to update their configuration settings.
    User must have an active session.
    
    Expects JSON payload with:
        to (str): Recipient contact information (phone number/email)
        signalType (str): Type of trigger used
        action (str): chosen action, either: "call", "message", "whatsapp", "email" or "log"

    Returns:
        A JSON response with either:
        - Success message and HTTP 200 status on successful update
        - Error message and HTTP 401 status if user is not logged in
        - Error message and HTTP 400 status if the request is malformed
    """
    if not session.get("userid"):
        return jsonify({
            'error': "User not logged in"
        }), 401
    try:
        requestJSON = request.get_json()
        if requestJSON['action'] == "call" or requestJSON['action'] == "message" or requestJSON['action'] == "whatsapp":
            if not isValidUKMobileNumber(requestJSON['to']):
                return jsonify({
                    'error': "Invalid mobile number"
                }), 400
        newConfig = ConfigResolver()
        newConfig.save(session['userid'],requestJSON['action'],requestJSON['signalType'],requestJSON['message'],requestJSON['to'])
        return jsonify({
            'message': f"Config updated for User: {session['userid']}"
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 400
    

@app.route('/myActions', methods=['GET'])
def myActions():
    """
    Retrieve and display the configuration list for the authenticated user.

    Renders a template showing all configurations for the
    currently logged-in user. The user must have an active session.

    Returns:
        Success: Rendered myActions.html template with the user's configuration data
        If unauthenticated: Redirect to login page
        If error occurs: JSON response with error message and HTTP 400 status code
    """
    if not session.get("userid"):
        return redirect("/login")
    try:
        newResolver = ConfigResolver()
        actionsList = newResolver.getmyActions(session['userid'])
        return render_template('myActions.html', active_page='myActions', actionsList=actionsList)
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 400


@app.route('/deleteConfig', methods=['POST'])
def deleteConfig():
    """
    Deletes a specific configuration (identified by userID) for the current
    user. Verifies both the configuration existence and user ownership before 
    deletion.The user must have an active session.
    
    Expects a JSON payload with:
        id (str): The unique identifier of the configuration to delete

    Returns:
        JSON response with either:
        - Success message with HTTP 204 status on successful deletion
        - Error message with HTTP 404 status if no matching config is found
        - Error message with HTTP 400 status for invalid requests
        - Error message with HTTP 401 status if user is not authenticated
    """
    requestJSON = request.get_json()
    objectID = requestJSON['id']
    try: 
        newResolver = ConfigResolver()
        deleteCount = newResolver.deleteConfig(session['userid'], objectID)
        if deleteCount == 0:
            return jsonify({
                'error': "No config found for this user"
            }), 404
        else:
            return jsonify({
                'message': f"Config deleted for User: {session['userid']}"
            }), 204
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 400

@app.route('/testContactDetails', methods=['POST'])

def testContactDetails():
    """
    Send a test notification to verify contact details.
    Validates contact details before sending.
    Requires valid user session.

    Expects a JSON payload with:
        to (str): Recipient contact information (phone number/email)
        signalType (str): Type of trigger used
        action (str): chosen action, either: "call", "message", "whatsapp", "email" or "log"

    Returns JSON response with either:
        - Success message and HTTP 200 on successful test
        - Error message and HTTP 400 for an invalid UK mobile number or invalid request parameters 
    """
    try:
        requestJSON = request.get_json()
        to = requestJSON['to']
        signalType = requestJSON['signalType']
        action = requestJSON['action']
        ts = pd.Timestamp.now()
        body = "This is a test message"
        if action == "call" or action== "message" or action == "whatsapp":
            if not isValidUKMobileNumber(requestJSON['to']):
                return jsonify({
                    'error': "Invalid mobile number"
                }), 400
        newProcessor = EventProcessor(session['userid'], signalType, ts)
        newProcessor.processContactDetailsTest(action, body, to)
        return jsonify({
            'message': "Test Message sent, please check your device"
        }), 200
    except Exception as e:
        return jsonify({
            'error': "Error sending test message"
        }), 400


@app.route('/event', methods=['POST'])
def eventStart():
    """
    Process and handle a new event triggered by a Flic button

    Expects a JSON payload with:
        signalType (str): Type of signal triggering the event
        userID (str): Identifier of the user triggering the event
        
    Returns:
        JSON response with either:
        - Success message containing event details with HTTP 200 status on successful processing.
        - Error message with HTTP 400 status if request is invalid.


    """
    try:
        requestJSON = request.get_json() 
        if requestJSON['signalType'] == 'flic':
            newEvent = FlicEventListener(requestJSON['userID'])
            newEvent.showData() #for testing purposes
            newEvent.sendData()
            return jsonify({
                'message': f"New Event Processed: {newEvent.getsignalType()} for User: {newEvent.getuserID()} at {newEvent.getTS()}"
            }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 400


@app.route('/login', methods=['POST'])
def login():
    """
    Authenticates the user and establishes a session by verifying user credentials 
    against stored records in database.
    Uses bcrypt for secure password verification.

    Expects a JSON payload with:
        email (str): User's registered email address
        password (str): User's password (will be securely verified)

    Returns:
        JSON response with either:
        - Confirmation message with user ID and HTTP 200 status
        - Error message with HTTP 401 status for invalid credentials
        or HTTP 400 status for malformed requests or server errors
    """
    try:
        requestJSON = request.get_json() 
        newResolver = UserResolver()
        password = requestJSON['password'].encode('utf-8')
        user = newResolver.getUserByEmail(requestJSON['email'])
        if user != None: 
            result = bcrypt.checkpw(password, user['password']) 
            if result:
                session["userid"] = str(user['_id'])
                session['role'] = user["role"]
                redirect = ""
                if user["role"] == "admin":
                    redirect="/dashboard/admin"
                else:
                    redirect="/addActions"
                return jsonify({'message': f'Logged in as {session["userid"]}', 'redirect' : redirect}), 200
            else:
                return jsonify({
                    'error': "Incorrect password"
                }), 401
        else:
            return jsonify({
                'error': "Incorrect password"
            }), 401   
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 400


@app.route('/logout', methods=['POST'])
def logout():
    """
    Terminates the current user session and redirects to login page.

    Returns:
        Redirects to the login page. Invalidates current session.
    """
    session["userid"] = None
    session["role"] = None
    return redirect("/login")


@app.route('/helplines', methods=['GET'])
def helplines():
    """
    Generate and display risk assessment recommendations for the authenticated user

    Returns:
        If authenticated: Rendered recommendations.html template
        If unauthenticated: Redirect to /login
    """
    if not session.get("userid"):
        return redirect("/login")
    else:
        newAnalysis = Analyser(session['userid'])
        riskScore = newAnalysis.calcRiskScore()
        risk = None
        if riskScore < 5:
            risk = "low"
        elif riskScore >= 5 and riskScore <= 10:
            risk = "medium"
        elif riskScore >= 10 and riskScore <= 20:
            risk = "high"
        else:
            risk = "critical"
    return render_template('recommendations.html', active_page='helplines', risk=risk)


# global variable for visualiser
visualiser = None

def create_dashboard_layout(userID):
    global visualiser
    visualiser = Dashboard(userID)
    if userID == None:
        return html.Div(
            children=[
                html.Nav(
                    children=[
                    html.Div(
                        className="container",
                        children=[
                            html.Header(
                                className="d-flex flex-wrap align-items-center justify-content-center justify-content-md-between py-3 mb-4 border-bottom",
                                children=[
                                    html.Ul(
                                        className="nav nav-pills col-12 col-md-auto mb-2 justify-content-center mb-md-0",
                                        children=[
                                            html.Li(className="nav-item", children=html.A("Home", href="/", className="nav-link px-2")),
                                            html.Li(className="nav-item", children=html.A("Admin Dashboard", href="/dashboard/admin", className="nav-link px-2 active")),
                                        ]
                                    ),
                                    html.Div(
                                        className="col-md-3 text-end",
                                        children=[
                                            html.Ul(
                                                className="nav nav-pills col-12 col-md-auto mb-2 justify-content-center mb-md-0",
                                                children=[
                                                    html.Li(className="nav-item", children=html.A("Logout", href="/logout", className="nav-link px-2"))
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]    
                ) 
                ]),
                html.Div(
                    children=[
                        dcc.Dropdown(
                            id='time-range-dropdown',
                            options=[
                                {'label': 'All Time', 'value': 'all_time'},
                                {'label': 'Current Week', 'value': 'current_week'}
                            ],
                            value='all_time',
                            style={'width': '50%', 'margin': 'auto'}
                        ),
                        dcc.Graph(id='activity-linechart', figure=visualiser.activityLineChart()),
                        dcc.Graph(id='time-popularity-by-hour', figure=visualiser.timePopularityByHour()),
                        dcc.Graph(id='frequency-in-week', figure=visualiser.frequencyInWeek()),
                        dcc.Graph(id='cumulative-events-chart', figure=visualiser.cumulativeEventsOverTime()),
                        
                    ]
                )                     
            ]
        )

    else:
        return html.Div(
            children=[
                html.Nav(
                    children=[
                    html.Div(
                        className="container",
                        children=[
                            html.Header(
                                className="d-flex flex-wrap align-items-center justify-content-center justify-content-md-between py-3 mb-4 border-bottom",
                                children=[
                                    html.Ul(
                                        className="nav nav-pills col-12 col-md-auto mb-2 justify-content-center mb-md-0",
                                        children=[
                                            html.Li(className="nav-item", children=html.A("Home", href="/", className="nav-link px-2")),
                                            html.Li(className="nav-item", children=html.A("Add Actions", href="/addActions", className="nav-link px-2")),
                                            html.Li(className="nav-item", children=html.A("My Actions", href="/myActions", className="nav-link px-2")),
                                            html.Li(className="nav-item", children=html.A("Helplines", href="/helplines", className="nav-link px-2")),
                                            html.Li(className="nav-item", children=html.A("Dashboard", href="/dashboard/", className="nav-link px-2 active")),
                                            html.Li(className="nav-item", children=html.A("Help", href="/help", className="nav-link px-2")),
                                        ]
                                    ),
                                    html.Div(
                                        className="col-md-3 text-end",
                                        children=[
                                            html.Ul(
                                                className="nav nav-pills col-12 col-md-auto mb-2 justify-content-center mb-md-0",
                                                children=[
                                                    html.Li(className="nav-item", children=html.A("Logout", href="/logout", className="nav-link px-2"))
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]    
                ) 
                ]),
                html.Div(
                    children=[
                        dcc.Dropdown(
                            id='time-range-dropdown',
                            options=[
                                {'label': 'All Time', 'value': 'all_time'},
                                {'label': 'Current Week', 'value': 'current_week'}
                            ],
                            value='all_time',
                            style={'width': '50%', 'margin': 'auto'}
                        ),
                        dcc.Graph(id='activity-linechart', figure=visualiser.activityLineChart()),
                        dcc.Graph(id='time-popularity-by-hour', figure=visualiser.timePopularityByHour()),
                        dcc.Graph(id='frequency-in-week', figure=visualiser.frequencyInWeek()),
                        dcc.Graph(id='cumulative-events-chart', figure=visualiser.cumulativeEventsOverTime()),
                        
                    ]
                )                     
            ]
        )
    

dash_app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@dash_app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/dashboard/':
        if not session.get('userid'):
            return html.Div("Please login to access the dashboard", style={'textAlign': 'center', 'marginTop': '20%'})
        return create_dashboard_layout(session.get('userid'))
    elif pathname == '/dashboard/admin':
        if not session.get('role') == 'admin':
            return html.Div("Unauthorised access", style={'textAlign': 'center', 'marginTop': '20%'})
        return create_dashboard_layout(None)
    return html.Div("Page not found", style={'textAlign': 'center', 'marginTop': '20%'})



#update graph for selected history range
@dash_app.callback(
    [Output('activity-linechart', 'figure'),
        Output('frequency-in-week', 'figure'),
        Output('time-popularity-by-hour', 'figure'),
        Output('cumulative-events-chart', 'figure')],
    [Input('time-range-dropdown', 'value')]
)
def update_graphs(selected_range):
    if visualiser:
        filter_week = (selected_range == 'current_week')
        return (
            visualiser.activityLineChart(filter_week=filter_week),
            visualiser.frequencyInWeek(filter_week=filter_week),
            visualiser.timePopularityByHour(filter_week=filter_week),
            visualiser.cumulativeEventsOverTime(filter_week=filter_week)
        )
    return {}, {}, {}, {}

if __name__ == '__main__':
    app.run(debug=True)
