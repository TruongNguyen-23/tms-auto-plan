from Server.Process.Handle.handle_file import save_file
from datetime import datetime,timedelta
import random
class TimeLineRoute:
    def __init__(self):
        print('Time Line Route')
        self.formatTime="%Y-%m-%d %H:%M:%S"
        self.formatEndTime="%Y-%m-%d, %H:%M:%S"
        self.nameTimeLine=""
    def calStartTimeLine(self,time):
        startTime=datetime.strptime(time,self.formatTime) + timedelta(minutes=10)
        endTime=datetime.strptime(time,self.formatTime) + timedelta(minutes=20)
        return startTime,endTime
    def calEndTimeLine(self,endTime):
        timeStart=datetime.strptime(endTime,self.formatEndTime) + timedelta(minutes=20)
        timeEnd=datetime.strptime(endTime,self.formatEndTime) +timedelta(minutes=40)
        return timeStart,timeEnd
    def saveFileTimeLine(self,data,fileName):
        nameFile=f"timeline{self.nameTimeLine}"
        save_file(data,nameFile)
    def setValueEndTime(self,time):
        time[-1][0]=datetime.strptime(time[-1][1],self.formatEndTime).replace(second=0)
        time[-1][1]=time[-1][0] + timedelta(seconds=30)
        time[-1][0]=str(datetime.strftime(time[-1][0],self.formatEndTime))
        time[-1][1]=str(datetime.strftime(time[-1][1],self.formatEndTime))
        return time
    def getCssTimeLine(self):
        with open('teamplates\csstimeline.css', 'r') as file:
            content = file.read()
        return content
    def setValueStartTime(self,data):
        def setData():
            data[0][1]=datetime.strptime(data[0][1],self.formatEndTime)+timedelta(seconds=30)
            data[0][1]=str(datetime.strftime(data[0][1],self.formatEndTime))
        if data[1][0]== data[0][0] and data[1][1] == data[0][1]:
            setData()
            data[1][0]=data[0][0]
            data[1][1]=data[0][1]
        else:
            setData()
        return data
    def cssReturnEndTime(self,time,modeReturn):
        if modeReturn == True:
            css=f"""#evt-{len(time)}{{width: 40px !important;}}"""
        else:
            css=""
        return css
    def ruleModeReturn(self,data,mode):
        if mode == True:
            self.setValueStartTime(data)
            self.setValueEndTime(data)
            return data
        else:
            self.setValueStartTime(data)
            return data
    def showDataTimeLine(self,startTime,endTime,data,fileName,modeReturn,endWork,timeName):
        self.nameTimeLine=timeName
        _data=self.ruleModeReturn(data,modeReturn)
        _timeData=self.updateNumberTimeLine(_data)
        cssTimeLine=self.getCssTimeLine()
        listTimeLine=self.showListTimeLine(_timeData,endWork)
        contentHTML=self.htmlContent(startTime,endTime,cssTimeLine,listTimeLine,fileName,_data,modeReturn,_timeData)
        return contentHTML
    def updateNumberTimeLine(self,data):
        interval_dict = {}
        for i, interval in enumerate(data):
            start_time, end_time = interval
            interval_tuple = tuple(interval)
            if interval_tuple in interval_dict:
                interval_dict[interval_tuple].append(i + 1)
            else:   
                interval_dict[interval_tuple] = [i + 1]
        dataResult = []
        for interval, numbers in interval_dict.items():
            dataResult.append([interval[0], interval[1], '-'.join(map(str, numbers))])
        return dataResult
    def showListTimeLine(self,_data,timeEnd):
        formatTime = '%Y-%m-%d %H:%M:%S'
        listTimeLine=""
        for index,item in enumerate(_data):
            item[1]=item[1].replace(",", "")
            changeColor=datetime.strptime(item[1], formatTime) > timeEnd
            listTimeLine+=f'<li data-popup="Start: {item[0][12:17]} - End: {item[1][11:16]} {"(Out working time)" if changeColor == True else "(In working time)"}" data-timeline-node="{{ start:\'{item[0]}\',end:\'{item[1]}\',row:1,bgColor: \'{ "#ffff00" if changeColor == True else "green"}\',color: \'{ "black" if changeColor == True else "#fff"}\'}}">{item[2]}</li>'
        return listTimeLine
    def htmlContent(self,startTime,endTime,cssTimeLine,listTimeLine,fileName,time,modeReturn,timeLenght):
        html=f"""
            <!DOCTYPE html>
            <html lang="en">

            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css"integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
                <title>Time Line Route</title>
            </head>

            <body>
                <div id="myTimeline">
                    <ul class="timeline-events">
                        {listTimeLine}
                    </ul>
                </div>
                <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
                <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
                <script src="https://cdn.jsdelivr.net/gh/ka215/jquery.timeline@master/dist/jquery.timeline.min.js"></script>
                <style>
                    {cssTimeLine}
                    {self.cssReturnEndTime(timeLenght,modeReturn)}
                </style>
                <script>

                    $(function () {{
                        $("#myTimeline").Timeline({{
                            startDatetime: '{startTime}',
                            endDatetime: '{endTime[:10]} 23:59:59',
                            rows: 3,    
                            scale: "hour",
                            minGridSize: 200,
                            datetimeFormat: {{ meta: 'H:m A' }},
                            rangeAlign: 'left',
                            width: 1800,
                            ruler: {{
                                top: {{
                                    height: 26,
                                    fontSize: 12,
                                    locale: "en-GB",
                                    format: {{ hour: "fulltime" }}
                                }},
                            }},
                            headline: {{
                                    display: false,
                                    locale: "en-GB",
                                    format: {{ custom: "%d/%m/%Y" }}
                                }},
                        }});
                        //Draw line form start to end trip
                        var nodeStart = $('div.jqtl-event-node:first-child');
                        var nodeEnd = $('div.jqtl-event-node:last-child');
                        nodeStart.addClass('line-from-start-to-end');
                        $('head').append('<style>.line-from-start-to-end::before{{width:'+ (nodeEnd.position().left - nodeStart.position().left + 1 ) +'px !important;}}</style>');
                        function getElementRawByIndex(index) {{
                            if ($.isNumeric(index)) {{
                                var arrNodeRaw = $('.timeline-events').children();

                                if (arrNodeRaw && arrNodeRaw.length > 0) {{
                                    for (let i = 0; i < arrNodeRaw.length; i++) {{
                                        if (parseInt(arrNodeRaw[i].innerText) === index) {{
                                            return arrNodeRaw[i].getAttribute('data-popup')
                                        }}
                                    }}
                                }}
                            }}  
                            return 'No Data';
                        }}
                        var arrNode = $('.jqtl-event-node');
                        console.log("Number of nodes : ", arrNode.length);
                        for (let index = 0; index < arrNode.length; index++) {{
                            var indexText = $(arrNode[index]).children('div.jqtl-event-label')[0].innerHTML;
                            var infoStartEnd = getElementRawByIndex(parseInt(indexText))
                            $(arrNode[index]).attr('data-container', 'body');
                            $(arrNode[index]).attr('data-toggle', 'popover');
                            $(arrNode[index]).attr('data-placement', 'top');
                            $(arrNode[index]).attr('data-content', infoStartEnd);
                        }}
                        $('[data-toggle="popover"]').popover({{trigger: 'hover' }});
                        
                        // refesh css layout
                        $(".jqtl-loading").css("left", "0");
                        window.scrollTo({{ top: 0, behavior: 'smooth'}});
                        
                    }})
                </script>
            </body>

            </html>
        """
        self.saveFileTimeLine(html,fileName)
        return html