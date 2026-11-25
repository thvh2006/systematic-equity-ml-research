"""Small auditable NYSE session calendar for the declared 2017–2026 scope."""
from datetime import date,timedelta,datetime
from zoneinfo import ZoneInfo
def easter(y):
 a=y%19;b=y//100;c=y%100;d=b//4;e=b%4;f=(b+8)//25;g=(b-f+1)//3;h=(19*a+b-d-g+15)%30;i=c//4;k=c%4;l=(32+2*e+2*i-h-k)%7;m=(a+11*h+22*l)//451
 return date(y,(h+l-7*m+114)//31,(h+l-7*m+114)%31+1)
def nth(y,m,weekday,n):
 d=date(y,m,1);return d+timedelta(days=(weekday-d.weekday())%7+7*(n-1))
def observed(d):return d+timedelta(days=-1 if d.weekday()==5 else 1 if d.weekday()==6 else 0)
def holidays(y):
 if not 2017<=y<=2026:raise ValueError('Calendar only reviewed for 2017–2026')
 jan=date(y,1,1);mem=date(y,6,1)-timedelta(days=1)
 while mem.weekday()!=0:mem-=timedelta(days=1)
 h={nth(y,1,0,3),nth(y,2,0,3),easter(y)-timedelta(days=2),mem,observed(date(y,7,4)),nth(y,9,0,1),nth(y,11,3,4),observed(date(y,12,25))}
 if jan.weekday()!=5:h.add(observed(jan))
 if y>=2022:h.add(observed(date(y,6,19)))
 if y==2018:h.add(date(2018,12,5))
 if y==2025:h.add(date(2025,1,9))
 return h
def sessions(start,end):
 d=date.fromisoformat(start);stop=date.fromisoformat(end);out=[]
 while d<=stop:
  if d.weekday()<5 and d not in holidays(d.year):out.append(d.isoformat())
  d+=timedelta(days=1)
 return out
def available_timestamp(day):
 # A conservative 16:15 ET signal time also follows 13:00 early closes.
 return datetime.fromisoformat(day+'T16:15:00').replace(tzinfo=ZoneInfo('America/New_York')).isoformat()
