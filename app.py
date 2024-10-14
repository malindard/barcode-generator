import streamlit as st
import pandas as pd
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import zipfile
import os
from io import BytesIO

# Fungsi untuk membuat barcode dan menambahkan teks
def create_barcode(name, number):
    # Ganti '/' dengan '_' untuk nama file barcode
    name_file = name.replace('/', '_')

    # Membuat barcode
    my_code = Code128(number, writer=ImageWriter())
    options = {'quiet_zone': 4} # ukuran white area
    barcode_result = f"{name_file}"
    my_code.save(barcode_result, options)

    # Menampilkan barcode
    barcode_path = f"{name_file}.png"
    img = Image.open(barcode_path)
    draw = ImageDraw.Draw(img)

    # Parameter teks
    font_size = 20
    try:
        font = ImageFont.truetype('Arial.ttf', font_size)
    except:
        font = ImageFont.load_default()

    text = f"{name}"
    # Bounding box untuk menentukan posisi teks di bawah barcode
    bbox = draw.textbbox((0,0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (img.width - text_width) // 2
    text_y = img.height - text_height - 10

    # Menambahkan teks ke gambar barcode
    draw.text((text_x, text_y), text, font=font, fill='black')

    # Menyimpan gambar yang sudah ditambahkan teks
    img.save(barcode_path)

    return barcode_path

# Membuat template Excel
def create_template():
    df_template = pd.DataFrame({
        'name_produk': ['Produk A', 'Produk B'],
        'barcode': ['123456789012', '987654321098']
    })
    return df_template

def main():
    st.title("Linda's Barcode Generator")

    # Tombol untuk download template
    st.subheader("Download Template (jika belum punya)")

    # Buat template excel
    df_template = create_template()

    # Simpan template ke dalam buffer agar dapat diunduh
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_template.to_excel(writer, index=False, sheet_name='Template')
        writer.close()

    # Tombol unduh template
    st.download_button(
        label='Download Template Excel',
        data=buffer,
        file_name='barcode_template.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # Upload file excel
    st.subheader('Upload File Excel')
    file_excel = st.file_uploader('Upload Excel File', type=['xlsx'])

    if file_excel:
        df = pd.read_excel(file_excel)

        # Menampilkan data excel
        st.dataframe(df)

        # Menyiapkan folder untuk menyimpan barcodes
        if not os.path.exists('barcodes'):
            os.makedirs('barcodes')

        # Iterasi setiap baris dan buat barcode
        for index, row in df.iterrows():
            name = row['nama_produk']
            number = str(row['barcode'])
            barcode_path = create_barcode(name, number)

            # Menampilkan barcode
            st.image(barcode_path, caption=f"Barcode {name}")

        # Buat ZIP untuk semua barcode
        zip_filename = 'barcodes.zip'
        with zipfile.ZipFile(zip_filename, 'w') as zip_file:
            for root, _, files in os.walk('.'):
                for file in files:
                    if file.endswith('.png'):
                        zip_file.write(os.path.join(root, file))

        # Tombol unduh ZIP file
        with open(zip_filename, 'rb') as f:
            st.download_button('Download ZIP barcodes', f, file_name=zip_filename)

if __name__ == "__main__":
    main()