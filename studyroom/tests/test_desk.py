from studyroom import desk, store, models
from datetime import datetime

def test_desk_checkin_staff_reason():
    # Δοκιμή ότι το check-in από υπάλληλο καταγράφει αιτιολογία και υπάλληλο (Φ6)
    student = store.add_student("s99", "Test Student", accessibility=False)
    room = store.add_room("A-01", 4)
    booking = store.create_booking("s99", "A-01", datetime.now(), hours=1)
    
    # Εκτέλεση check-in από υπάλληλο λόγω βλάβης QR
    updated_booking = desk.desk_checkin(booking.id, "s99", staff_id="admin1", reason="Βλάβη QR - Ταυτοποίηση με πάσο")
    
    assert updated_booking.status == models.CHECKED_IN
    assert updated_booking.checkin_reason is not None