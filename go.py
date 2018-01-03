# Brian Cain 2018
# A simple python script to get myfitnesspal data
# and export it to Google Sheets

from datetime import date, timedelta, datetime
import collections
import myfitnesspal
import json
import yaml

def calculate_macros(data):
    # print '{:.1%}'.format(carbs/total)
    macros = collections.OrderedDict()
    for i in data:
        # convert macros from grams to calories
        carbs = float(i.totals['carbohydrates'] * 4)
        fats = float(i.totals['fat'] * 9)
        protein = float(i.totals['protein'] * 4)

        total = carbs + fats + protein
        macros[i.date] = {"carbs": carbs/total, "fat": fats/total, "protein": protein/total}

    return macros

def get_data(mfp_client, start_date):
    d1 = start_date
    d2 = date.today()
    delta = d2 - d1
    data = []
    missed_dates = []

    print "Retrieving data from myfitnesspal....this will take a while...\n"
    for i in range(delta.days + 1):
        local_date = d1 + timedelta(days=i)
        print "Getting date " + str(local_date) + " . . ."

        # terribad try/catch because the myfitnesspal api is super unstable
        try:
            mfp_data = mfp_client.get_date(local_date)
        except IndexError as e:
            print e
            print "Could not get date . . . continuing anyway . . ."
            missed_dates.append(local_date)
            continue
        except:
            print "Something went wrong :("
            raise

        data.append(mfp_data)

    if len(missed_dates) > 0:
        print
        print "Could not get information for these dates:"
        print missed_dates
        print

    return data

def get_login():
    with open("login.yaml", "r") as stream:
        try:
            login_info = yaml.load(stream)
            return login_info
        except yaml.YAMLError as exc:
            print exc
            exit(1)

def save_mfp_data(data):
    with open('mfpdata.json', 'wb') as outfile:
            json.dump(data, outfile)

def main():
    login_info = get_login()
    # 4 weeks ago
    #start_date = datetime.now() - timedelta(days=28)
    #start_date = start_date.date()
    start_date = date(2018, 1, 1) # test date

    print "Logging in as " + login_info['username'] + "..."
    client = myfitnesspal.Client(login_info['username'], login_info['password'])
    print "Done!"

    body_weights = client.get_measurements('Weight', start_date)
    data = get_data(client, start_date)
    macros = calculate_macros(data)
    print macros


if __name__ == '__main__':
    main()
