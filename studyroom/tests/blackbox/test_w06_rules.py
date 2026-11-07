from datetime import datetime
import pytest
from studyroom import BookingError, create_booking, cancel_booking, check_in

# Το fixture `now` από το conftest.py είναι Τρίτη 3/11/2026, 10:00
TUE = (2026, 11, 3)
MON = (2026, 11, 2)
SAT = (2026, 11, 7)

def at(day, h, m=0, s=0):
    return datetime(*day, h, m, s)

#  TC-BB-01 έως TC-BB-05: ΚΡ1 Ωράριο Καθημερινής 
@pytest.mark.parametrize("hour, hours, ok, tc_id", [
    (7, 1, False, "TC-BB-01"),  # 07:00 (πριν το άνοιγμα)
    (8, 1, True,  "TC-BB-02"),  # 08:00 (άνοιγμα)
    (21, 1, True, "TC-BB-04"),  # 21:00 (1 ώρα, λήγει 22:00)
    (22, 1, False, "TC-BB-05"), # 22:00 (μετά το κλείσιμο)
])
def test_kr01_weekday_hours(now, hour, hours, ok, tc_id):
    start = at(TUE, hour)
    if ok:
        assert create_booking("1001", "Α-1", start, hours, now=now).status == "active"
    else:
        with pytest.raises(BookingError):
            create_booking("1001", "Α-1", start, hours, now=now)

#  TC-BB-17 έως TC-BB-19: ΚΡ9 Όρια Check-in 
@pytest.mark.parametrize("m, s, ok, tc_id", [
    (14, 59, True, "TC-BB-17"), # 14' 59'' μετά (έγκυρο)
    (15, 0,  True, "TC-BB-18"), # 15' 00'' (όριο)
    (15, 1,  False,"TC-BB-19"), # 15' 01'' (άκυρο, χαμένη)
])
def test_kr09_checkin_window(now, m, s, ok, tc_id):
    start = at(TUE, 12, 0) # Κράτηση στις 12:00
    booking = create_booking("1001", "Α-1", start, 1, now=now)
    checkin_time = at(TUE, 12, m, s)
    
    if ok:
        check_in(booking.id, "1001", now=checkin_time)
        assert booking.status == "checked_in"
    else:
        with pytest.raises(BookingError):
            check_in(booking.id, "1001", now=checkin_time)

#  TC-BB-21, 23: ΚΡ3 Ημερήσιο Όριο 2 ωρών (κανονική περίοδος) 
def test_kr03_daily_limit(now):
    # Ο φοιτητής κλείνει 2 ώρες
    create_booking("1002", "Α-2", at(TUE, 12), 2, now=now)
    # Πάει να κλείσει άλλη 1 ώρα (Σύνολο 3 > 2) -> TC-BB-23
    with pytest.raises(BookingError):
        create_booking("1002", "Α-3", at(TUE, 15), 1, now=now)

#  TC-BB-26: ΚΡ7 Συγκρούσεις επικαλυπτόμενων κρατήσεων 
def test_kr07_conflict(now):
    # Πρώτη κράτηση 12:00-14:00
    create_booking("1003", "Α-4", at(TUE, 12), 2, now=now)
    # TC-BB-26: Δεύτερη κράτηση 13:00-14:00 (Σύγκρουση)
    with pytest.raises(BookingError):
        create_booking("1004", "Α-4", at(TUE, 13), 1, now=now)

#  TC-BB-30, 31: Αρνητικός έλεγχος Εξουσιοδότησης 
def test_negative_authorization(now):
    booking = create_booking("1005", "Α-1", at(TUE, 14), 1, now=now)
    
    # TC-BB-30: Φοιτητής 1006 προσπαθεί να ακυρώσει την κράτηση του 1005
    with pytest.raises(BookingError):
        cancel_booking(booking.id, "1006", now=now)