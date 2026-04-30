/**
 * CRAVVY — Order Sync Apps Script
 * ==================================
 *
 * Paste this into your Google Sheet's Apps Script editor
 * (Extensions → Apps Script → replace Code.gs contents with this).
 *
 * Then deploy as a Web App:
 *   - Deploy → New deployment
 *   - Type: Web app
 *   - Execute as: Me
 *   - Who has access: Anyone (REQUIRED — even anonymous, no login)
 *   - Click Deploy → copy the URL
 *
 * Set that URL as the GOOGLE_SHEET_WEBHOOK_URL env var on your Flask app.
 *
 * Every checkout = one new row in your Sheet, instantly. No setup beyond this.
 */

const SHEET_NAME = 'Orders';   // tab name in your Sheet — will be created if missing

// Column headers — first time the script runs, these get written
const HEADERS = [
  'Timestamp',
  'Order #',
  'Customer Name',
  'Email',
  'Phone',
  'Address',
  'City',
  'State',
  'Pincode',
  'Payment Method',
  'Items',
  'Item Count',
  'Subtotal (₹)',
  'Shipping (₹)',
  'Total (₹)',
  'Status'
];

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);

    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = ss.getSheetByName(SHEET_NAME);

    // Create sheet + headers on first run
    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
      sheet.getRange(1, 1, 1, HEADERS.length)
        .setFontWeight('bold')
        .setBackground('#FFE600')
        .setBorder(true, true, true, true, true, true);
      sheet.setFrozenRows(1);
    }

    // Map payload → row
    const row = [
      new Date(data.timestamp || new Date()),
      data.order_number || '',
      data.customer_name || '',
      data.customer_email || '',
      data.customer_phone || '',
      data.address || '',
      data.city || '',
      data.state || '',
      data.pincode || '',
      data.payment_method || '',
      data.items_summary || '',
      data.item_count || 0,
      data.subtotal || 0,
      data.shipping || 0,
      data.total || 0,
      data.status || 'pending'
    ];

    sheet.appendRow(row);

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true, row: sheet.getLastRow() }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet() {
  // For testing — opens in browser shows it's alive
  return ContentService
    .createTextOutput('CRAVVY Orders endpoint is live. POST orders here.')
    .setMimeType(ContentService.MimeType.TEXT);
}
