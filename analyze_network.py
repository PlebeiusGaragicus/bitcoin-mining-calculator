# GET DATA
## CONNECT TO NODE
## TRY TO LOAD FILE
## VERIFY FILE IS INTACT
## CONTINUE LOADING DATA TO UPDATE FILE
## SAVE FILE IF ANY NEW DATA WAS SAVED

# GRAPH DATA FROM/TO ANY POINT IN HISTORY
## CALCULATE SMA, EMA WITH ARBITRARY VARIABLES AND GRAPH
## FIND LINE OF BEST FIT

# PROJECT AND GRAPH EXPECTED FUTURE BASED ON ANY ARBITRARY POINT IN TIME
## VERIFY PROJECTIONS AGAINST REAL DATA (WHILE BACKTESTING)


import csv
import pandas
import logging

CSV_DATA_FILENAME = './network_history.csv'

def make_empty_datafile():
    with open(CSV_DATA_FILENAME, mode='w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['height', 'hashrate', 'difficulty'])

def return_dataframe_of_data_file():
    try:
        with open(CSV_DATA_FILENAME, mode='r') as csv_file:
            df = pandas.read_csv(csv_file)

            starting = df['height'].to_numpy()[0]
            ending = df['height'].to_numpy()[-1]

            #logging.debug(df.to_string())
            logging.debug(f"starting height in datafile: {starting}")
            logging.debug(f"ending height in data file: {ending}")
    except FileNotFoundError as e:
        logging.exception("no data file found - creating a blank one...")
        make_empty_datafile()
    except KeyError:
        logging.exception("This data file may be mal-formatted... re-creating")
        make_empty_datafile()
    except IndexError:
        logging.exception("This data file looks empty")

        return None




def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] (%(filename)s @ %(lineno)d) %(message)s",
        handlers=[logging.StreamHandler(),
        logging.FileHandler('debug.log', mode='w')])

    df = return_dataframe_of_data_file()

    print(df.to_string())

        # #header, *rows=[row for row in reader]
        # # is this the most efficient way?  Should I be doing this?
        # #rows = [row for row in reader]

        # for row in reader:
        #     print(row[0])
        #     data['height'].append( row[0] )
        #     data['hashrate'].append( row[1] )
        #     data['difficulty'].append( row[2] )
    
    # check total lines of file and compare with block_header


    #for bh in 
    #    f"{block_height}, {block_hashrate}, {block_difficulty}"

if __name__ == '__main__':
    main()
