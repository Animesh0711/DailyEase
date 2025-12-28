from fastapi import APIRouter
import calendar

router = APIRouter()


@router.get("/api/calendar/structured/{year}")
def get_structured_calendar(year: int):
    """Return a structured calendar for the given year.
    Response format:
    { "year": 2025, "months": [ {"month":1, "name":"January", "weeks": [[0,0,1,2,3,4,5], ... ] }, ... ] }
    """
    cal = calendar.Calendar(firstweekday=0)  # Monday=0 by default
    months = []
    month_names = [calendar.month_name[i] for i in range(1,13)]
    for m in range(1, 13):
        weeks = calendar.monthcalendar(year, m)
        months.append({
            "month": m,
            "name": month_names[m-1],
            "weeks": weeks
        })

    return {"year": year, "months": months}


@router.get("/api/calendar/text/{year}")
def get_text_calendar(year: int):
    """Return a formatted text calendar for the year (same as Python calendar.calendar).
    Useful for display or download.
    """
    txt = calendar.calendar(year, w=3, l=1, c=6)
    return {"year": year, "text": txt}
