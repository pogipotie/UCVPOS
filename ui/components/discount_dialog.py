from PyQt6.QtCore import Qt, QPoint, QStringListModel
from PyQt6.QtGui import QColor, QFont, QCursor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QRadioButton, QButtonGroup,
    QMessageBox, QFrame, QGraphicsDropShadowEffect, QCompleter,
    QStackedWidget, QWidget, QTextEdit, QApplication
)
from ui.styles import Styles
from repositories.customer_repo import customer_repo

from database.models import Customer

class DiscountDialog(QDialog):
    def __init__(self, parent=None, discount_type=None):
        super().__init__(parent)
        # Frameless styling
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(550, 650) 
        
        self.selected_type = discount_type # SC or PWD (required)
        self.customer = None # The resolved customer object
        
        self.search_mode = True # Track current view
        self._drag_pos = None
        
        self.init_ui()
        
    def init_ui(self):
        # Main Container
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.container = QFrame()
        self.container.setObjectName("dialogContainer")
        self.container.setStyleSheet("""
            QFrame#dialogContainer {
                background-color: #161B22; 
                border: 1px solid #30363D;
                border-radius: 0px;
            }
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)
        
        layout.addWidget(self.container)
        
        # Content Layout
        c_layout = QVBoxLayout(self.container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(0)
        
        # 1. Header
        header = self.create_header()
        c_layout.addWidget(header)
        
        # 2. Tabs / Toggles
        tabs_container = QFrame()
        tabs_container.setFixedHeight(50)
        tabs_container.setStyleSheet("background-color: #0D1117; border-bottom: 1px solid #30363D;")
        tabs_layout = QHBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(0)
        
        self.btn_tab_search = QPushButton("🔍 Search Existing")
        self.btn_tab_new = QPushButton("➕ New Customer")
        
        for btn in [self.btn_tab_search, self.btn_tab_new]:
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(50)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: transparent;
                    color: #8B949E;
                    font-weight: 600;
                    font-size: 14px;
                    border-bottom: 2px solid transparent;
                }
                QPushButton:checked {
                    color: #FFFFFF;
                    border-bottom: 2px solid #E94560;
                    background-color: #161B22;
                }
                QPushButton:hover:!checked {
                    color: #C9D1D9;
                    background-color: #21262D;
                }
            """)
            tabs_layout.addWidget(btn)
            
        self.btn_tab_search.setChecked(True)
        self.btn_tab_search.clicked.connect(lambda: self.switch_tab(0))
        self.btn_tab_new.clicked.connect(lambda: self.switch_tab(1))
        
        c_layout.addWidget(tabs_container)
        
        # 3. Stacked Content
        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_search_view())
        self.stack.addWidget(self.create_new_view())
        
        c_layout.addWidget(self.stack)
        
        # 4. Footer Actions
        footer = QFrame()
        footer.setStyleSheet("border-top: 1px solid #30363D; background-color: #0D1117;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFixedSize(100, 40)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #30363D;
                border-radius: 0px;
                color: #C9D1D9;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #21262D;
                border-color: #8B949E;
            }
        """)
        
        self.btn_apply = QPushButton("Apply Discount")
        self.btn_apply.setFixedHeight(40)
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apply.clicked.connect(self.validate_and_accept)
        self.btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                border-radius: 0px;
                border: none;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #2EA043;
            }
            QPushButton:pressed {
                background-color: #238636;
            }
        """)
        
        footer_layout.addWidget(btn_cancel)
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_apply)
        
        c_layout.addWidget(footer)

        # Draggable header
        header.mousePressEvent = self.mousePressEvent
        
        if self.selected_type:
            self.update_header()

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("background-color: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 0, 25, 0)
        
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        
        self.lbl_title = QLabel("Apply Discount")
        self.lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        
        self.lbl_subtitle = QLabel("Select or register customer")
        self.lbl_subtitle.setStyleSheet("font-size: 12px; color: #8B949E;")
        
        title_box.addStretch()
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_subtitle)
        title_box.addStretch()
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(32, 32)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.reject)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8B949E;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover { color: #FFFFFF; }
        """)
        header_layout.addWidget(btn_close)
        
        return header

    def update_header(self):
        if self.selected_type == "SC":
            self.lbl_title.setText("Senior Citizen Discount")
            self.lbl_Title_color = "#FFB800" # Not using this var directly but logic implies
            self.lbl_subtitle.setText("RA 9994 - 20% Discount + VAT Exemption")
        elif self.selected_type == "PWD":
            self.lbl_title.setText("PWD Discount")
            self.lbl_subtitle.setText("RA 10754 - 20% Discount + VAT Exemption")

    def create_search_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Search Box
        lbl = QLabel("SEARCH CUSTOMER (ID or NAME)")
        lbl.setStyleSheet("color: #8B949E; font-size: 11px; font-weight: bold;")
        layout.addWidget(lbl)
        
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Type name or ID number...")
        self.txt_search.setFixedHeight(45)
        self.txt_search.setStyleSheet(Styles.INPUT_STYLE)
        
        # Setup Completer
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.activated.connect(self.on_completer_activated)
        self.txt_search.textChanged.connect(self.update_suggestions)
        self.txt_search.returnPressed.connect(self.on_search_enter)
        self.txt_search.setCompleter(self.completer)
        
        layout.addWidget(self.txt_search)
        
        # Result Card (Initially Hidden or Placeholder)
        self.result_card = QFrame()
        self.result_card.setObjectName("resultCard")
        self.result_card.setVisible(False)
        self.result_card.setStyleSheet("""
            #resultCard {
                background-color: #0D1117;
                border: 1px solid #30363D;
                border-left: 4px solid #238636;
                border-radius: 0px;
            }
        """)
        rc_layout = QVBoxLayout(self.result_card)
        rc_layout.setContentsMargins(20, 15, 20, 15)
        
        self.lbl_found_name = QLabel()
        self.lbl_found_name.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        
        self.lbl_found_id = QLabel()
        self.lbl_found_id.setStyleSheet("font-size: 14px; color: #E94560; font-family: monospace;")
        
        rc_layout.addWidget(self.lbl_found_name)
        rc_layout.addWidget(self.lbl_found_id)
        
        # Address & Contact
        self.lbl_found_address = QLabel()
        self.lbl_found_address.setStyleSheet("font-size: 13px; color: #C9D1D9; margin-top: 4px;")
        self.lbl_found_address.setWordWrap(True)
        rc_layout.addWidget(self.lbl_found_address)
        
        self.lbl_found_contact = QLabel()
        self.lbl_found_contact.setStyleSheet("font-size: 13px; color: #8B949E;")
        rc_layout.addWidget(self.lbl_found_contact)
        
        layout.addWidget(self.result_card)
        
        # Warning Label
        self.lbl_warning = QLabel("Customer not found. Please switch to 'New Customer' tab.")
        self.lbl_warning.setVisible(False)
        self.lbl_warning.setStyleSheet("color: #E94560; font-style: italic; margin-top: 10px;")
        layout.addWidget(self.lbl_warning)
        
        layout.addStretch()
        return page

    def create_new_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        # ID
        layout.addWidget(self.create_label("ID NUMBER (REQUIRED)"))
        self.txt_new_id = self.create_input("Enter ID Number")
        layout.addWidget(self.txt_new_id)
        
        # Name
        layout.addWidget(self.create_label("FULL NAME (REQUIRED)"))
        self.txt_new_name = self.create_input("Enter Full Name")
        layout.addWidget(self.txt_new_name)
        
        # Address
        layout.addWidget(self.create_label("ADDRESS (OPTIONAL)"))
        self.txt_address = self.create_input("Enter Address")
        layout.addWidget(self.txt_address)
        
        # Contact
        layout.addWidget(self.create_label("CONTACT NUMBER (OPTIONAL)"))
        self.txt_contact = self.create_input("Enter Mobile/Phone")
        layout.addWidget(self.txt_contact)
        
        layout.addStretch()
        return page

    def create_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #8B949E; font-size: 11px; font-weight: bold;")
        return lbl
        
    def create_input(self, placeholder):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(40)
        inp.setStyleSheet(Styles.INPUT_STYLE)
        return inp

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        self.search_mode = (index == 0)
        
        self.btn_tab_search.setChecked(index == 0)
        self.btn_tab_new.setChecked(index == 1)
        
        if index == 0:
            self.txt_search.setFocus()
        else:
            self.txt_new_id.setFocus()

    def update_suggestions(self, text):
        if len(text) < 2:
            return
        
        # Pass self.selected_type to search
        results = customer_repo.search(text, limit=10, customer_type=self.selected_type)
        suggestions = [f"{c.name} | {c.id_number} | {c.type}" for c in results]
        model = QStringListModel(suggestions)
        self.completer.setModel(model)
        
        # Reset selection if typing changes
        # Use lower() for case-insensitive check
        if self.customer:
             c_name = self.customer.name.lower()
             c_id = str(self.customer.id_number).lower() # ID might be numeric
             txt_lower = text.lower()
             
             if c_name not in txt_lower and c_id not in txt_lower:
                 self.customer = None
                 self.result_card.setVisible(False)

    def on_completer_activated(self, text):
        try:
            name, id_num, c_type = text.split(" | ")
            # Validate type match
            if self.selected_type and c_type != self.selected_type:
                # If mismatch, we can either warn or allow switching
                # Warn for now as the dialog is initiated with a type
                 QMessageBox.warning(self, "Type Mismatch", 
                                     f"Selected customer is {c_type}, but you are applying {self.selected_type} discount.")
                 self.txt_search.clear()
                 return

            self.customer = customer_repo.get_by_id_number(id_num, c_type)
            if self.customer:
                self.show_found_customer(self.customer)
                self.lbl_warning.setVisible(False)
        except:
            pass

    def on_search_enter(self):
        """Handle Enter key in search box"""
        text = self.txt_search.text().strip()
        if not text:
            return
            
        # If completer is visible, let it handle? 
        # But returnPressed usually fires before completer activated if user hits enter quickly.
        
        # Check if we already have a selected customer that matches text
        if self.customer and (self.customer.name in text or self.customer.id_number in text):
            self.validate_and_accept()
            return

        # Try to find exact match
        # 1. Try ID exact match
        c = customer_repo.get_by_id_number(text, self.selected_type)
        if c:
            self.customer = c
            self.show_found_customer(c)
            self.lbl_warning.setVisible(False)
            return
            
        # 2. Try parsing "Name | ID | Type" format (if user typed/pasted full string)
        if " | " in text:
            parts = text.split(" | ")
            if len(parts) >= 2:
                # Format: Name | ID | Type
                # Try ID (index 1)
                id_part = parts[1].strip()
                c = customer_repo.get_by_id_number(id_part, self.selected_type)
                if c:
                    self.customer = c
                    self.show_found_customer(c)
                    self.lbl_warning.setVisible(False)
                    # Loop back to validate logic effectively? 
                    # No, this just finds it. User might hit enter again or we can accept immediately?
                    # Standard behavior: Find first, then user Hits enter again or clicks Apply.
                    # But if we want Enter to Apply...
                    # If we found it, maybe we should just accept() if it was Enter key?
                    # The function is on_search_enter. 
                    # If we found it now, we should probably fall through to validation/accept?
                    # CURRENT LOGIC: 'on_search_enter' finds and sets self.customer. 
                    # It DOES NOT call accept() unless self.customer WAS ALREADY SET at start.
                    return
                
                # Try Name (index 0)
                name_part = parts[0].strip()
                results = customer_repo.search(name_part, limit=1, customer_type=self.selected_type)
                if results:
                    c = results[0]
                    self.customer = c
                    self.show_found_customer(c)
                    self.lbl_warning.setVisible(False)
                    return

        # 3. Try Name search (get first result)
        results = customer_repo.search(text, limit=1, customer_type=self.selected_type)
        if results:
            c = results[0]
            # Verify type
            if self.selected_type and c.type != self.selected_type:
                 QMessageBox.warning(self, "Type Mismatch", 
                                     f"Found {c.name} ({c.type}), but you are applying {self.selected_type}.")
                 return
                 
            self.customer = c
            self.show_found_customer(c)
            self.lbl_warning.setVisible(False)
        else:
            self.lbl_warning.setVisible(True)
            self.result_card.setVisible(False)
            self.customer = None
            
    def show_found_customer(self, customer):
        self.lbl_found_name.setText(customer.name)
        self.lbl_found_id.setText(f"ID: {customer.id_number}")
        
        # Show address/contact if available
        addr = customer.address if customer.address else "No address"
        contact = customer.contact_number if customer.contact_number else "No contact"
        
        self.lbl_found_address.setText(f"📍 {addr}")
        self.lbl_found_contact.setText(f"📞 {contact}")
        
        self.result_card.setVisible(True)
        self.txt_search.setText(f"{customer.name} | {customer.id_number}")

    def validate_and_accept(self):
        if self.search_mode:
            # SEARCH MODE
            if not self.customer:
                # Fallback: Try to resolve from text one last time
                # This handles cases where user typed exact ID but didn't hit Enter
                text = self.txt_search.text().strip()
                if text:
                    # 1. Try Exact ID
                    c = customer_repo.get_by_id_number(text.split(" | ")[0].strip(), self.selected_type)
                    if not c:
                        # 2. Try strict name search? No, risky. 
                        # But if they selected from completer, text has |, so maybe split?
                        if " | " in text:
                             parts = text.split(" | ")
                             if len(parts) >= 2:
                                 # Try ID from parts
                                 potential_id = parts[1].strip()
                                 c = customer_repo.get_by_id_number(potential_id, self.selected_type)
                    
                    if c:
                         self.customer = c
                
            if not self.customer:
                self.lbl_warning.setVisible(True)
                QMessageBox.warning(self, "Customer Not Found", 
                                    "Please select an existing customer from the search or switch to 'New Customer' to register.")
                return
            
            # Use self.customer
            # Map to dialog properties expected by caller
            self.selected_type = self.customer.type
            self.id_number = self.customer.id_number
            self.customer_name = self.customer.name
             # Customer ID is internal, repo has it.
            self.accept()
            
        else:
            # NEW MODE
            id_num = self.txt_new_id.text().strip()
            name = self.txt_new_name.text().strip()
            
            if not id_num or not name:
                QMessageBox.warning(self, "Missing Fields", "ID Number and Name are required.")
                return
                
            # Check duplicates handled by repo or check here?
            existing = customer_repo.get_by_id_number(id_num, self.selected_type)
            if existing:
                 QMessageBox.warning(self, "Duplicate ID", f"Customer with ID {id_num} already exists.")
                 return
            
            # Create
            new_c = Customer(
                name=name,
                id_number=id_num,
                type=self.selected_type,
                address=self.txt_address.text().strip(),
                contact_number=self.txt_contact.text().strip()
            )
            
            created = customer_repo.create(new_c)
            if created:
                self.customer = created
                self.selected_type = created.type
                self.id_number = created.id_number
                self.customer_name = created.name
                self.accept()
            else:
                QMessageBox.critical(self, "Database Error", "Failed to save new customer.")

    # Allow window dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def keyPressEvent(self, event):
        """Prevent closing on Enter"""
        if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            # Check focus
            focused = QApplication.focusWidget()
            if isinstance(focused, QLineEdit):
                # Let inputs handle their own returnPressed signals
                # but do NOT propogate to QDialog.accept
                return
        super().keyPressEvent(event)
