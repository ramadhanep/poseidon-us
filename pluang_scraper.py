import requests
import csv

# Base URL API Pluang
base_url = 'https://pluang.com/_next/data/dashboard_Nr8hqeCYmy/id/explore/usstocks/{}.json?category=usstocks&page={}'

# Nama file output CSV
csv_filename = 'pluang_us_stocks.csv'

# Buka file CSV untuk menulis data
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Tulis header
    writer.writerow(['symbol', 'name', 'icon'])

    # Loop dari halaman 1 sampai 57
    for page in range(1, 58):
        url = base_url.format(page, page)
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Ambil assetCategories
            asset_categories = data.get('pageProps', {}).get('data', {}).get('assetCategories', [])

            for category in asset_categories:
                # Ambil assetCategoryData
                asset_category_data = category.get('assetCategoryData', [])

                for subcategory in asset_category_data:
                    assets = subcategory.get('assets', [])

                    for stock in assets:
                        tile_info = stock.get('tileInfo', {})
                        symbol = tile_info.get('symbol', 'N/A')
                        name = tile_info.get('name', 'N/A')
                        icon_url = tile_info.get('icon', 'N/A')

                        # Tulis ke CSV
                        writer.writerow([symbol, name, icon_url])

            print(f'Halaman {page} berhasil diproses.')
        else:
            print(f'Gagal mengambil data dari halaman {page}. Status code: {response.status_code}')

print(f'Data selesai disimpan di {csv_filename}')
