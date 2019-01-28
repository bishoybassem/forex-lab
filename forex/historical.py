import requests
import re
import os
import zipfile
from forex.config import DATA_PATH, PAIRS


HIST_DATA_URL = 'http://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/{}/{}'
CSV_FILE = 'DAT_ASCII_{}_M1_{}.csv'


def pair_string(pair):
    return ''.join(pair).lower()


def year_month(year, month=None, sep=''):
    if month is None:
        return str(year)
    return '{}{}{:02d}'.format(year, sep, month)


def create_data_directory(pair):
    output_path = os.path.join(DATA_PATH, pair_string(pair))
    if not os.path.exists(output_path):
        os.makedirs(output_path)


def get_archive_path(pair, year, month=None):
    return os.path.join(DATA_PATH, pair_string(pair), '{}.zip'.format(year_month(year, month)))


def download_hist_data(pair, year, month=None):
    print('Downloading', pair, 'data for', year, month)
    url = HIST_DATA_URL.format(pair_string(pair), year_month(year, month, sep='/'))
    response = requests.get(url)
    assert response.status_code == 200
    match_tk = re.search(r'id="tk" value="(.{32})"', str(response.content))
    assert match_tk
    data = {'tk': match_tk.group(1),
            'date': str(year),
            'datemonth': year_month(year, month),
            'platform': 'ASCII',
            'timeframe': 'M1',
            'fxpair': pair_string(pair)}
    response = requests.post(url='http://www.histdata.com/get.php', data=data, headers={'Referer': url})
    assert response.status_code == 200

    with open(get_archive_path(pair, year, month), 'wb') as file:
        file.write(response.content)


def get_prices(pair, year, month=None):
    create_data_directory(pair)
    archive_path = get_archive_path(pair, year, month)
    if os.path.exists(archive_path):
        print(archive_path, 'already exists, skipping download!')
    else:
        download_hist_data(pair, year, month)

    csv_file = CSV_FILE.format(pair_string(pair).upper(), year_month(year, month))
    lines = zipfile.ZipFile(archive_path).open(csv_file).readlines()
    lines_utf8 = map(lambda l: l.decode('utf8').strip(), lines)
    lines_filtered = filter(lambda l: l.startswith(str(year)), lines_utf8)
    return list(lines_filtered)


def merge_all_pairs(year, month=None):
    all_prices_dict = {}
    for i in range(len(PAIRS)):
        price_entries = get_prices(PAIRS[i], year, month)
        for entry in price_entries:
            parts = entry.split(';')
            timestamp = parts[0]
            close_price = parts[-2]
            if timestamp not in all_prices_dict:
                all_prices_dict[timestamp] = [None] * len(PAIRS)
            all_prices_dict[timestamp][i] = close_price

    timestamps = list(all_prices_dict.keys())
    timestamps.sort()
    return [[timestamp] + all_prices_dict[timestamp] for timestamp in timestamps]


def fill_gaps(entries):
    for i in range(1, len(entries)):
        for j in range(1, len(entries[i])):
            if entries[i][j] is None:
                entries[i][j] = entries[i - 1][j]


def merge_all_pairs_to_file(file_name, year, month=None):
    merged_entries = merge_all_pairs(year, month)
    fill_gaps(merged_entries)
    print('Adding merged pair prices for', year, month, 'to', file_name)
    with open(file_name, 'a') as file:
        for entry in merged_entries:
            if None not in entry:
                file.write(';'.join(entry))
                file.write(os.linesep)


def prepare_data(from_year, to_year, to_month=None):
    out_file = os.path.join(DATA_PATH, '{}_{}'.format(year_month(from_year), year_month(to_year, to_month)))
    if os.path.exists(out_file):
        print(out_file, 'already exists, skipping generation!')
        return

    for year in range(from_year, to_year):
        merge_all_pairs_to_file(out_file, year)
    if to_month is not None:
        for month in range(1, to_month):
            merge_all_pairs_to_file(out_file, to_year, month)


if __name__ == "__main__":
    prepare_data(2015, 2019)
