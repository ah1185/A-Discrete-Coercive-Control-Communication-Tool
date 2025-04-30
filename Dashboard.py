
import plotly.express as px
import pandas as pd
from AnalysisResolver import AnalysisResolver


class Dashboard:
    def __init__(self,userID):
        resolver = AnalysisResolver(userID)
        series = resolver.getTimestamp()
        self.values = series
        
        
    def cumulativeEventsOverTime(self, filter_week=False):
        df = pd.DataFrame({
            'Date': self.values.dt.normalize(),  #removes time component
            'Timestamp': self.values
        })
        
        if filter_week:
            now = pd.Timestamp.now()
            startOfWeek = now.floor('D') - pd.Timedelta(days=now.dayofweek) #uses floor to get that start of Monday
            endOfWeek = startOfWeek + pd.Timedelta(days=6, hours=23, minutes=59, seconds=59, milliseconds=999)
            df = df[(df['Timestamp'] >= startOfWeek) & (df['Timestamp'] <= endOfWeek)]
            if df.empty:
                print("No data for the current week.")
                return px.line(title='No Data for Current Week')
            time_group = df['Date'].value_counts().sort_index()
            title_suffix = ' (Current Week)'
        else:
            time_group = self.values.dt.to_period('D').value_counts().sort_index()
            time_group.index = time_group.index.to_timestamp()
            title_suffix = ' (All Time)'
        
        cumulative = time_group.cumsum()
        
        fig = px.area(
            x=cumulative.index,
            y=cumulative.values,
            title=f'Cumulative Events Over Time{title_suffix}',
            labels={'x': 'Date', 'y': 'Total Events'}
        )
        
        fig.update_layout(
            title_x=0.5,
            hovermode='x unified',
            yaxis_title='Total Events',
            xaxis_title='Date'
        )
        
        if filter_week:
            fig.update_xaxes(
                tickformat='%A',  #show day names for weekly view
                tickvals=cumulative.index
            )
        else:
            fig.update_xaxes(
                tickformat='%b %Y'  #show month/year for all-time view
            )
        
        return fig

    def timePopularityByHour(self, filter_week=False):
        df = pd.DataFrame({
            'Hour': self.values.dt.hour,
            'Timestamp': self.values  
        })

        if filter_week:
            now = pd.Timestamp.now()
            startOfWeek = now.floor('D') - pd.Timedelta(days=now.dayofweek)
            endOfWeek = startOfWeek + pd.Timedelta(days=6, hours=23, minutes=59, seconds=59, milliseconds=999)
            df = df[(df['Timestamp'] >= startOfWeek) & (df['Timestamp'] <= endOfWeek)]
            if df.empty:
                print("No data for the current week.")
                return px.bar(title='No Data for Current Week')
    
            # Debug prints
            print(f"Filtering between: {startOfWeek} and {endOfWeek}")
            print("Sample timestamps:", df['Timestamp'].head())


        frequency = df['Hour'].value_counts().sort_index()
        df_counts = pd.DataFrame({
            'Hour': frequency.index,
            'Frequency': frequency.values
        })

        fig = px.bar(
            df_counts,
            x='Hour',
            y='Frequency',
            title='Most Popular Times by Hour' + (' (Current Week)' if filter_week else ' (All Time)'),
            labels={'Hour': 'Time of Day', 'Frequency': 'Frequency'},
            color='Frequency',
            color_continuous_scale='Plasma'
        )
        fig.update_xaxes(
            tickvals=list(range(24)),
            ticktext=[f'{h}:00' for h in range(24)],
            tickangle=-45
        )
        fig.update_layout(title_x=0.5)
        return fig
    

    def frequencyInWeek(self, filter_week=False):
        df = pd.DataFrame({
            'Day': self.values.dt.strftime('%A'),
            'Timestamp': self.values  
        })

        if filter_week:
            now = pd.Timestamp.now()
            startOfWeek = now.floor('D') - pd.Timedelta(days=now.dayofweek)
            endOfWeek = startOfWeek + pd.Timedelta(days=6, hours=23, minutes=59, seconds=59, milliseconds=999)
            df = df[(df['Timestamp'] >= startOfWeek) & (df['Timestamp'] <= endOfWeek)]
            if df.empty:
                print("No data for the current week.")
                return px.bar(title='No Data for Current Week')

        week_counts = df['Day'].value_counts()
        df_counts = pd.DataFrame({
            'Day': week_counts.index,
            'Frequency': week_counts.values
        })

        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df_counts['Day'] = pd.Categorical(df_counts['Day'], categories=day_order, ordered=True)
        df_counts = df_counts.sort_values('Day')

        fig = px.bar(
            df_counts,
            x='Day',
            y='Frequency',
            title='Frequency by Day of the Week' + (' (Current Week)' if filter_week else ' (All Time)'),
            labels={'Day': 'Day of the Week', 'Frequency': 'Frequency'},
            color='Frequency',
            color_continuous_scale='Plasma'
        )
        fig.update_xaxes(tickangle=-45)
        fig.update_layout(title_x=0.5)
        return fig

    def activityLineChart(self, filter_week=False):
        df = pd.DataFrame({
            'Day': self.values.dt.strftime('%A'),
            'Hour': self.values.dt.hour,
            'Timestamp': self.values  
        })

        if filter_week:
            now = pd.Timestamp.now()
            startOfWeek = now.floor('D') - pd.Timedelta(days=now.dayofweek)
            endOfWeek = startOfWeek + pd.Timedelta(days=6, hours=23, minutes=59, seconds=59, milliseconds=999)
            df = df[(df['Timestamp'] >= startOfWeek) & (df['Timestamp'] <= endOfWeek)]
            df = df[(df['Timestamp'] >= startOfWeek) & (df['Timestamp'] <= endOfWeek)]
            if df.empty:
                print("No data for the current week.")
                return px.line(title='No Data for Current Week')

        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df['Day'] = pd.Categorical(df['Day'], categories=day_order, ordered=True)
        grouped_data = df.groupby(['Day', 'Hour']).size().reset_index(name='Count')

        fig = px.line(
            grouped_data,
            x='Hour',
            y='Count',
            color='Day',
            title='Activity Trends by Hour and Day of the Week' + (' (Current Week)' if filter_week else ' (All Time)'),
            labels={'Hour': 'Hour of the Day', 'Count': 'Number of Events', 'Day': 'Day of the Week'}
        )

        fig.update_yaxes(title_text='Number of Events')
        fig.update_layout(title_x=0.5) 
        fig.update_xaxes(
            tickvals=list(range(24)),
            ticktext=[f'{h}:00' for h in range(24)],
            tickangle=-45,
            title_text='Hour of the Day'
        )
        return fig
