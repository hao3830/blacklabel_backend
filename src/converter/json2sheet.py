import os
import json
import shutil

import xlsxwriter


def json2sheet(json_fpath, sheet_fpath):
    with open(json_fpath, "r") as jf:
        vdict = json.loads(jf.read())

    headers = list(vdict[0].keys())

    workbook = xlsxwriter.Workbook(sheet_fpath)
    worksheet = workbook.add_worksheet()

    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    for row, item in enumerate(vdict[0:]):
        for col, header in enumerate(headers):
            worksheet.write(row + 1, col, item[header])

    workbook.close()


def json2sheet_db(json_folder, sheet_folder):
    if not os.path.exists(sheet_folder):
        os.mkdir(sheet_folder)
    else:
        shutil.rmtree(sheet_folder)
        os.mkdir(sheet_folder)

    for json_fname in os.listdir(json_folder):
        json_fname_woext = json_fname.split(".")[0]
        json_fpath = os.path.join(json_folder, json_fname)

        sheet_fname = "%s.xlsx" % json_fname_woext
        sheet_fpath = os.path.join(sheet_folder, sheet_fname)

        json2sheet(json_fpath, sheet_fpath)


def main():
    json_folder = ""
    sheet_folder = ""
    json2sheet_db(json_folder, sheet_folder)


if __name__ == "__main__":
    main()
