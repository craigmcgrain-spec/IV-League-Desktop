from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox
)
from ..database import models


class CompanyInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Company Information")
        self.setMinimumWidth(400)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setLabelAlignment(__import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.AlignmentFlag.AlignRight)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Company Name")
        form.addRow("Company Name:", self.name_edit)

        self.street_edit = QLineEdit()
        self.street_edit.setPlaceholderText("Street Address")
        form.addRow("Street:", self.street_edit)

        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("City")
        form.addRow("City:", self.city_edit)

        self.zip_edit = QLineEdit()
        self.zip_edit.setPlaceholderText("Zip Code")
        form.addRow("Zip:", self.zip_edit)

        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("(555) 555-5555")
        form.addRow("Phone:", self.phone_edit)

        self.contact_name_edit = QLineEdit()
        self.contact_name_edit.setPlaceholderText("Contact Person")
        form.addRow("Contact Name:", self.contact_name_edit)

        self.contact_email_edit = QLineEdit()
        self.contact_email_edit.setPlaceholderText("email@example.com")
        form.addRow("Contact Email:", self.contact_email_edit)

        layout.addLayout(form)

        btn_row = QVBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _load_data(self):
        info = models.get_company_info()
        self.name_edit.setText(info.get("name", ""))
        self.street_edit.setText(info.get("street", ""))
        self.city_edit.setText(info.get("city", ""))
        self.zip_edit.setText(info.get("zip", ""))
        self.phone_edit.setText(info.get("phone", ""))
        self.contact_name_edit.setText(info.get("contact_name", ""))
        self.contact_email_edit.setText(info.get("contact_email", ""))

    def _save(self):
        info = {
            "name": self.name_edit.text().strip() or "The IV League II",
            "street": self.street_edit.text().strip(),
            "city": self.city_edit.text().strip(),
            "zip": self.zip_edit.text().strip(),
            "phone": self.phone_edit.text().strip(),
            "contact_name": self.contact_name_edit.text().strip(),
            "contact_email": self.contact_email_edit.text().strip(),
        }
        models.save_company_info(info)
        QMessageBox.information(self, "Saved", "Company information saved.")
        self.accept()
