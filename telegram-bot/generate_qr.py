import qrcode

# URL to encode
url = ['URL_TO_THE_BOT?start=question_1','URL_TO_THE_BOt?start=question_2']

# Generate QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

for i in range(0, len(url)):
    qr.add_data(url[i])
    qr.make(fit=True)

# Create an image from the QR code
    img = qr.make_image(fill='black', back_color='white')   
    img.save('telegram_qr_'+ str(i) + '.png')
