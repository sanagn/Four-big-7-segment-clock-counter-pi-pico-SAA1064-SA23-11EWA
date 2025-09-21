######################################################################################
# ΚΕΔΙΒΙΜ Πανεπιστημίου Κρήτης                                                       #
# Προγραμματισμός μικροελεγκτών Rasbperry Pi Pico με MicroPython                     #
# όνομα έργου: Ρολόϊ 4 μεγαλών 7-τμημάτων ψηφίων που παίρχει τον χρόνα απο εναν      #
#               ntp server  και το στέλνει στο SAA1064                               #
# Όνομα: Sanagn                                                                      #
# ημερομηνία: 7/9/2025                                                               #
# ειναι μια σύμτηξη ολω των άλλω αρχείων boot-main-saa1064                           # 
######################################################################################

# Raspberry Pi Pico και SAA1064 Digital Clock
from machine import Pin, I2C, RTC
import time
import socket
import network
from secret import ssid,password
import struct



NTP_DELTA = 2208988800
host = "pool.ntp.org"
'''
Η Greenwich Mean Time ειναι 2 ώρες πίσω από την ώρα στην Αθήνα όταν η Αθήνα
είναι σε κανονική ώρα, και 3 ώρες πίσω όταν η Αθήνα είναι σε καλοκαιρινή (daylight saving time).
'''

# --- Διαμόρφωση Υλικού ---
led = Pin("LED", Pin.OUT)
# Ορισμός ακροδεκτών I2C για το Pico.
# Οι GP4 (SDA0) και GP5 (SCL0) είναι κοινώς χρησιμοποιούμενοι ακροδέκτες I2C0.
SDA_PIN = 4
SCL_PIN = 5
# Διεύθυνση I2C του SAA1064.
# Συχνές διευθύνσεις είναι 0x70 (ADR pin to GND) ή 0x3B.
# Βεβαιωθείτε ότι αυτή η διεύθυνση ταιριάζει με τη διαμόρφωση του SAA1064 σας.
SAA1064_ADDRESS = 0x38
# εγκαινίαση του δίαυλου I2C.
# Χρησιμοποιούμε τον ελεγκτή I2C0 (0) με τους καθορισμένους ακροδέκτες και συχνότητα 100kHz.
i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=100000)  # alway freq=100000

# oper socket fich time for ntp
def set_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    t = val - NTP_DELTA    
    tm = list(time.gmtime(t))
    tm[3] = tm[3] + 3
    # προσθετουμε 3 για καλοκαιρ. ωρα Αθήνας
    # προσθετουμε 2 για χειμερ. ωρα Αθήνας    
    if tm[3]>=24: tm[3]=tm[3]-24
    RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    #                (year, month, day, weekday, hour, minute, second, subseconds)
    # Προσθέτει +1 στο tm[6] γιατί η MicroPython μετράει τις μέρες από 1 (Δευτέρα) αντί για 0
    # --- Αρχική Ρύθμιση Ώρας (Εκτελείται μόνο μία φορά για να ρυθμίσετε την ώρα) ---
    # Η μορφή είναι: (έτος, μήνας, ημέρα, ημέρα_της_εβδομάδας, ώρες, λεπτά, δευτερόλεπτα, υποδευτερόλεπτα)
    # Η ημέρα_της_εβδομάδας είναι 1=Δευτέρα, 7=Κυριακή. Το υποδευτερόλεπτα μπορεί να είναι 0 για απλότητα.
    # π.χ. rtc.datetime((2024, 10, 27, 7, 15, 30, 0, 0)) # Παράδειγμα: 27 Οκτωβρίου 2024, Κυριακή, 15:30:00

# Init Wi-Fi Interface
def init_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # Connect to your network
    wlan.connect(ssid, password)
    # Wait for Wi-Fi connection
    connection_timeout = 10
    while connection_timeout > 0:
        print(wlan.status())
        if wlan.status() >= 3:
            break
        connection_timeout -= 1
        print('Waiting for Wi-Fi connection...')
        time.sleep(1)
    # Check if connection is successful
    if wlan.status() != 3:
        print('Failed to connect to Wi-Fi')
        return False
    else:
        print('Connection successful!')
        network_info = wlan.ifconfig()
        print('IP address:', network_info[0])
        print(wlan)
        return True

# --- Κλάση Οδηγού SAA1064 ---
class SAA1064:
    def __init__(self, i2c_bus, address=0x38):
        self.i2c = i2c_bus
        self.address = address
        # Χάρτης τμημάτων για ψηφία 0-9, κενό και δεκαδική υποδιαστολή (κοινή άνοδος).
        # Κάθε byte αντιστοιχεί στα τμήματα G F E D C B A DP (MSB προς LSB).
        # Για παράδειγμα, 0x3F (00111111) ενεργοποιεί A, B, C, D, E, F για το 0.
        self._segment_map = {
            0: 0x3F,  # 0
            1: 0x06,  # 1
            2: 0x5B,  # 2
            3: 0x4F,  # 3
            4: 0x66,  # 4
            5: 0x6D,  # 5
            6: 0x7D,  # 6
            7: 0x07,  # 7
            8: 0x7F,  # 8
            9: 0x6F,  # 9
            'blank': 0x00, # Κενό ψηφίο
            'dp': 0x80   # Δεκαδική υποδιαστολή (bit 7)
        }
        # Το byte ελέγχου για δυναμική λειτουργία (C0=1) και προεπιλεγμένη ένταση (C4,C5,C6=000)
        # 0x10 = 0b00010000 (Static mode, default current)
        # 0x27 = 0b00100111 (Dynamic mode, 6mA current, C1=1, C2=1 - for blanking control)
        
        # Χρησιμοποιούμε 0x10 για απλή δυναμική λειτουργία.
        self._control_byte = 0x17 # Default control byte for dynamic mode
        self.init_display()

    def init_display(self):
        # Αρχή της οθόνης με ένα byte ελέγχου και καθαρισμό.
        # Το SAA1064 περιμένει το byte ελέγχου πρώτο, μετά τα δεδομένα ψηφίων.
        # Το byte ελέγχου 0x10 (0b00010000) ορίζει τη δυναμική λειτουργία.
        # Τα επόμενα 4 bytes είναι τα δεδομένα για τα 4 ψηφία.
        # Το 0x01 είναι το byte εντολής για πρόσβαση στους καταχωρητές δεδομένων.
        self.i2c.writeto(self.address, bytes([0x00, self._control_byte])) # Set control register
        self.clear() # Clear all segments

    def clear(self):
        # Στέλνει μηδενικά bytes για να σβήσει όλα τα τμήματα σε όλα τα ψηφία.
        # Το 0x01 είναι το byte εντολής για πρόσβαση στους καταχωρητές δεδομένων.
        # Αποστολή 4 bytes 0x00 για τα 4 ψηφία.
        self.i2c.writeto(self.address, bytes([0x01, 0x00, 0x00, 0x00, 0x00]))

    def set_intensity(self, level):
        # Ρυθμίζει την ένταση της οθόνης.
        # Το επίπεδο (level) είναι ένας ακέραιος από 0-7 (ή 0-3 ανάλογα την υλοποίηση).
        # Τα bits C4, C5, C6 του byte ελέγχου ελέγχουν το ρεύμα.
        # C4 (bit 4) = +3mA, C5 (bit 5) = +6mA, C6 (bit 6) = +12mA
        # Για απλότητα, θα χρησιμοποιήσουμε ένα μικρότερο εύρος ή προκαθορισμένα επίπεδα.
        # Εδώ, απλά ρυθμίζουμε το C0 (dynamic mode) και τα bits έντασης.
        # level 0: default (0mA added)
        # level 1: 0b00010000 | 0b00010000 = 0x10 (no extra current)
        # level 2: 0b00010000 | 0b00011000 = 0x18 (3mA added)
        # level 3: 0b00010000 | 0b00100000 = 0x20 (6mA added)
        # level 4: 0b00010000 | 0b00101000 = 0x28 (9mA added)
        # level 5: 0b00010000 | 0b01000000 = 0x40 (12mA added)
        # level 6: 0b00010000 | 0b01010000 = 0x50 (15mA added)
        # level 7: 0b00010000 | 0b01110000 = 0x70 (21mA added)

        # Βεβαιωθείτε ότι το level είναι εντός του επιτρεπτού εύρους (π.χ., 0-7)
        level = max(0, min(level, 7))
        
        # Κατασκευή του byte ελέγχου.
        # Ξεκινάμε με τη δυναμική λειτουργία (0x10) και προσθέτουμε τα bits έντασης.
        intensity_bits = 0
        if level & 0b001: # Check if bit 0 is set (3mA)
            intensity_bits |= (1 << 4)
        if level & 0b010: # Check if bit 1 is set (6mA)
            intensity_bits |= (1 << 5)
        if level & 0b100: # Check if bit 2 is set (12mA)
            intensity_bits |= (1 << 6)
        
        self._control_byte = 0x27 | intensity_bits
        self.i2c.writeto(self.address, bytes([0x00, self._control_byte]))

    def display_time(self, hours, minutes, show_colon=True):
        # Μορφοποιεί τις ώρες και τα λεπτά για εμφάνιση σε 4 ψηφία (HHMM).
        # Εξασφαλίζει μηδενικά στην αρχή (π.χ., 5 γίνεται 05).
        hours_str = "{:02d}".format(hours)
        minutes_str = "{:02d}".format(minutes)
        # Μετατροπή των ψηφίων σε μοτίβα τμημάτων.
        # Η σειρά των ψηφίων είναι D4, D3, D2, D1 (MSB προς LSB) για τον SAA1064.
        # Έτσι, για HHMM, στέλνουμε M2, M1, H2, H1.
        # (π.χ. για 12:34, στέλνουμε 4, 3, 2, 1)   
        digit_data = [
            self._segment_map[int(minutes_str[1])],  # Ψηφίο 4 (δεύτερο ψηφίο λεπτών)
            self._segment_map[int(minutes_str[0])],  # Ψηφίο 3 (πρώτο ψηφίο λεπτών)
            self._segment_map[int(hours_str[1])],    # Ψηφίο 2 (δεύτερο ψηφίο ωρών)
            self._segment_map[int(hours_str[0])]     # Ψηφίο 1 (πρώτο ψηφίο ωρών)
        ]

        # Προσθήκη άνω και κάτω τελείας.
        # Συχνά, η άνω και κάτω τελεία υλοποιείται χρησιμοποιώντας τη δεκαδική υποδιαστολή
        # ενός από τα ενδιάμεσα ψηφία (π.χ., το Ψηφίο 2, που είναι το δεύτερο ψηφίο ωρών).
        # Εδώ, θα χρησιμοποιήσουμε το DP του Ψηφίου 2 (το δεύτερο ψηφίο ωρών)
        # για να αναπαραστήσουμε την άνω και κάτω τελεία μεταξύ ωρών και λεπτών.      
        if show_colon:
            digit_data[2] |= self._segment_map['dp'] # Ενεργοποίηση DP στο Ψηφίο 2 (δεύτερο ψηφίο ωρών)

        # Αποστολή των δεδομένων στην οθόνη.
        # Το 0x01 είναι το byte εντολής για πρόσβαση στους καταχωρητές δεδομένων.
        print(hours_str, " / ", minutes_str)        
        self.i2c.writeto(self.address, bytes([0x01] + digit_data))



# --- Εγκαινίαση Οθόνης SAA1064 ---
saa1064_display = SAA1064(i2c, SAA1064_ADDRESS)
# Ρύθμιση έντασης (π.χ., επίπεδο 4 για μέτρια φωτεινότητα)
saa1064_display.set_intensity(2)

colon_state = True # Για αναβόσβημα της άνω και κάτω τελείας

init_wifi(ssid,password)

set_time()
# --- Κύριος Βρόχος Εφαρμογής ---    
while True:
    print(time.localtime())
    #current_time = rtc.datetime()
    current_time = time.localtime()
    hours = current_time[3]
    minutes = current_time[4]
    seconds = current_time[5]
    # Εμφάνιση της ώρας στην οθόνη SAA1064
    # Αναβόσβημα της τελείας κάθε δευτερόλεπτο
    saa1064_display.display_time(hours, minutes, show_colon=colon_state)
    colon_state = not colon_state # Εναλλαγή κατάστασης τελείας
    # Περιμένετε μέχρι το επόμενο δευτερόλεπτο
    time.sleep(1)