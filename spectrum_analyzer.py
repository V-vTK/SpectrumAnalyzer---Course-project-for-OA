import os
import numpy as np
import ikkunasto  as ik

# Ikkunasto as a bundled file
# pip install numpy, pip install matplotlib
# Current newest version of Python (3.10.6 64-bit) from the official site


app_state_dictionary = {
    "text_box": None,
    "graph_box" : [],
    "x_data" : [], #kinetic energy/binding energy
    "y_data" :  [], #intensity (arbitrary unit)
    "mouse_data" : [],
    "counter" : 1
}


def open_folder_as_list(): 
    """
    Opens a folder window UI using library: Ikkunasto. 
    User picks a folder and the files in the folder are printed into a list.
    if the user cancels and doesn't pick a folder the app prints an error message.

    :return: folder contents as a list
    :return: folder directory
    """

    folder = ik.avaa_hakemistoikkuna("File")
    try:
        folder_contents = os.listdir(folder)
    except FileNotFoundError as error:
        folder_contents = None
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"],f"Failed to open a folder. Error message was: {error}"
        )
    return folder_contents,folder


def check_files(folder_contents,folder):
    """
    Checks multiple files from given folder.
    Takes in measurement data from .txt files other files are skipped.
    The function checks the following things:
    Every row consists of exactly two parts separated by space " "
    The two parts are numbers that can be converted into floats, and are separated by".".

    if the whole file with all it's row passes:
    the first part is added to the measurement dictionary as an x-coordinate
    the second part is the y-measurement data,
    which is added to other y-data corresponding to the same x-coordinate.
    The following data is collected for easier troubleshooting:

    :param: folder contents list
    :param: folder directory
    :return: list of broken files
    :return: list of files with the wrong file extension
    :return: dictionary:  {key = x-data : item = y-data summed together}
    :return: list of files accepted files
    """

    correct_files_list = []
    measurement_dictionary = {}
    broken_file_list = []
    wrong_file_extension_list = []

    for file in folder_contents:
        file_extension_list = os.path.splitext(file)
        if file_extension_list[1] != ".txt":
            wrong_file_extension_list.append(file)
            ik.kirjoita_tekstilaatikkoon(
                app_state_dictionary["text_box"],
                f"File {file} was skipped: wrong file extension"
            )
            continue
        file_dir = os.path.join(folder,file)
        with open(file_dir,"r", encoding="utf=8") as current_file:
            temp_dictionary = {}
            for row in current_file:
                row = row.replace("\n", "")
                parts = row.split(" ")
                if len(parts) == 2: #if row consists of two parts seperated by space
                    try:
                        #if the parts are numbers add to temp_dictionary
                        temp_dictionary[float(parts[0])] = float(parts[1]) 
                    except ValueError: #if not skip the whole file
                        temp_dictionary = {}
                        broken_file_list.append(file)
                        ik.kirjoita_tekstilaatikkoon(
                            app_state_dictionary["text_box"],
                            f"Corrupted file '{file}' was skipped: Values are not numbers"
                        )
                        break
                else: #if not skip the whole file
                    temp_dictionary = {}
                    broken_file_list.append(file)
                    ik.kirjoita_tekstilaatikkoon(
                        app_state_dictionary["text_box"],
                        f"Corrupted file '{file}' was skipped: Row does not consist of two parts"
                    )
                    break
            if len(temp_dictionary) > 0: #if data was collected: file was not corrupted
                correct_files_list.append(file)
                if len(measurement_dictionary) == 0: #First time just copy
                    measurement_dictionary = temp_dictionary
                else:
                    for key in temp_dictionary: #After that combine with earlier values
                        measurement_dictionary[key] += temp_dictionary[key]
    return broken_file_list, wrong_file_extension_list, measurement_dictionary, correct_files_list


def data_to_xy_list(measurements_dictionary):
    """
    Takes in a dictionary and returns two lists:
    the dictionary keys are in the x-list
    the dictionary items are in the y-list

    :param: Dictionary with measurement data
    :return: x-list 
    :return: y-list
    """

    x_list = []
    y_list = []
    for key in measurements_dictionary:
        x_list.append(key)
        y_list.append(measurements_dictionary[key])
    return x_list, y_list  


def sub_open_folder(): 
    """
    Activates the functions in order to open, read and store measurement data.
    More information about the innerworkings inside the actual functions.

    After collecting the necessary data. 
    Informs the about the amount of passed files.

    The unused variables are collected for easier troubleshooting.
    """
    folder_contents_list, folder = open_folder_as_list()
    #broken_files_list,wrong_file_extension_list,correct_measurements_dictionary,correct_files_list
    if folder_contents_list is not None:
        _, _, correct_measurements_dictionary, correct_files_list = check_files(
            folder_contents_list,folder
        )
        x_data, y_data = data_to_xy_list(correct_measurements_dictionary)
        app_state_dictionary["x_data"] = x_data
        app_state_dictionary["y_data"] = y_data
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"],
            f"Found {len(correct_files_list)} files with viable data."
        )


def pick_datapoint(event): #
    """
    Takes mouse events and reads the x- and y-values. 
    The values are stored into the app state dictionary as tuples inside a list.
    The x- and y-coordinates are also printed out into a text box using Ikkunasto.
    
    :param: matplotlib mouse-event listener
    """

    x_data = event.xdata
    y_data = event.ydata
    my_tuple = (x_data,y_data)
    app_state_dictionary["mouse_data"].append(my_tuple)
    ik.kirjoita_tekstilaatikkoon(
        app_state_dictionary["text_box"],f"Data at mouse click was x = {x_data} and y = {y_data}"
    )


def plot_data():
    """
    Plots data into a graph using matplotlib.

    The used data is from the global app_state_dictionary.
    Likewise, the graph variable, which points to where graph should be,
    is stored inside the app_state_dictionary.

    if there is no usable data the function notifies the user
    using the UI textbox created by Ikkunasto.
    """

    graph = app_state_dictionary["graph_box"]
    x_list = app_state_dictionary["x_data"]
    y_list = app_state_dictionary["y_data"]
    graph[2].plot(x_list,y_list)
    graph[2].set_xlabel("Binding energy (eV)")
    graph[2].set_ylabel("Intensity (arbitrary unit)") #
    graph[0].draw()
    if not x_list:
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"], "No data has been given. Unable to plot the data"
        )


def clear_plot():
    """
    Additional functionality:
    This function clears the measurement data from the app state dictionary
    and updates the plot: emptying it
    Afterwards informs the user using the interface textbox.
    """

    graph = app_state_dictionary["graph_box"]
    app_state_dictionary["x_data"] = []
    app_state_dictionary["y_data"] = []
    graph[2].cla()
    graph[0].draw()
    ik.kirjoita_tekstilaatikkoon(
        app_state_dictionary["text_box"], "App data and plot was cleared"
    )


def save_as_png():
    """
    Opens a folder window UI using library: Ikkunasto. 
    User picks a location and name for the image.
    Saves the image of the current graph.
    Using the chosen folder with the chosen name as a .png file.

    if the user cancels and doesn't pick a location, the app prints an error message.
    """

    file_dir = ik.avaa_tallennusikkuna("Select filename and location")
    graph = app_state_dictionary["graph_box"]
    if file_dir != "":
        graph[0].print_figure(file_dir)
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"], "Picture saved succesfully"
        )
    else:
        ik.kirjoita_tekstilaatikkoon(app_state_dictionary["text_box"],
            "Unable to save picture: file directory not chosen"
        )


def prior_mouse_data():
    """
    Selects the last two entries from app state mouse data
    returns them as x1, y2 coordinates
    derived from data format: "[(x,y),(x,y),(x,y)]"

    if there is no mouse data informs the user trough the text box.

    :return: x1 mouse event coordinates - second to last
    :return: y1 mouse event coordinates - second to last
    :return: x2 mouse event coordinates - latest
    :return: y2 mouse event coordinates - latest
    """

    try:
        y_2 = app_state_dictionary["mouse_data"][-1][1]
        x_2 = app_state_dictionary["mouse_data"][-1][0]
        y_1 = app_state_dictionary["mouse_data"][-2][1]
        x_1 = app_state_dictionary["mouse_data"][-2][0]
        return x_1, y_1, x_2, y_2
    except IndexError:
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"],
            "Did not find last two selected datapoints, please select two datapoints"
        )   
        return False, False, False, False


def sort_between_values(x_1,x_2):
    '''
    The function takes in x-values (param) which are compared to the x-data (app_state_dictionary).
    The function finds the values between these two values and removes the data around these values
    The Y-data is sliced using the same indexes.
    
    if there is no data the user is informed and the function returns None, None

    :param: x1-value (float) (mouse input on the graph) 
    :param: x2-value (float) (mouse input on the graph)

    :return: sliced x-data (list)
    :return: sliced y-data (list)
    '''
    x_data = app_state_dictionary["x_data"]
    y_data = app_state_dictionary["y_data"]
    if not x_data:
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"], "No data selected, please import data"
        )
        return None, None

    if x_1 > x_2:
        x_1, x_2 = x_2, x_1
    for index, value in enumerate(x_data):
        if x_1 <= value and "start_value" not in locals():
            start_value = index
        if x_2 <= value and "stop_value" not in locals():
            stop_value = index
            break
    sliced_x_data = x_data[start_value : stop_value]
    sliced_y_data = y_data[start_value : stop_value]
    return sliced_x_data, sliced_y_data    


def integrate():
    '''
    If the user has clicked integrate or background remove button I.e. seen the guide message.

    The function collects the mouse data - last two clicked x-coordinates
    Slices the data lists around these points using a function: sort_between_values
    Calculates the integral for the sliced data using numpy.trapz (trapezoid rule)
    prints the calculated integral into the text box created by Ikkunasto

    else the function directs the user to pick two datapoints.
    '''
    if app_state_dictionary["counter"] % 2 == 0:
        x_1, _, x_2, _ = prior_mouse_data()
        sliced_x_list, sliced_y_list = sort_between_values(x_1,x_2)
        if sliced_x_list is not None and x_1 is not False:
            integral = np.trapz(sliced_y_list, x=sliced_x_list)
            ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"],f"the integral between selected points is {integral}"
        )
    else:
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"],
            "Now click two datapoints on the graph and click integrate again"
        )
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"],
            "Or use the last two datapoints by double-clicking integrate"
        )
    app_state_dictionary["counter"] = app_state_dictionary["counter"] +1


def calculate_line_equation(x_1,y_1,x_2,y_2):
    """
    Takes in four coordinates, calculates a linear equation using these points.
    The user is informed about the resulting equation 
    if the equation can not be calculated the user is once again informed
    and the function returns False, False
    else the function returns the slope (k) and the constant term (b).

    :param: x1 x-coordinate (float)
    :param: y1 y-coordinate (float)
    :param: x2 x-coordinate (float)
    :param: y2 y-coordinate (float)

    :return: slope (k) (float)
    :return: constant_term (b) (float)
    """
    if x_1 == x_2 and y_2 == y_1 and x_1 is not False:
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"],
            "You clicked the same point twice - unable to calculate"
        )
    elif x_1 != x_2 and y_2 == y_1 and x_1 is not False:
        slope = 0.0
        constant_term = ((x_2 * y_1) - (x_1 * y_2)) / (x_2 - x_1)
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"],
            f"The equation is: y = {slope}x + {constant_term}"
        )
    elif x_1 == x_2 and x_1 is not False:
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"],
            "The equation is vertical, unable to calculate"
        )
    elif x_1 is not False:
        slope = (y_2 - y_1) / (x_2 - x_1) #k
        constant_term = (x_2 * y_1 - x_1 * y_2) / (x_2 - x_1) #b
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"],
            f"The equation is: y = {slope}x + {constant_term}" # y = k*x + b
        )
    if "slope" in locals() and "constant_term" in locals():
        return slope, constant_term 
    return False, False #otherwise the can not be calculated


def calculate_data_by_equation(slope, constant_term):
    '''
    Calculates the y-values for given x-values using the given equation y = k*x + b
    Subtracts these new y-values from corresponding y-data.
    This is used for removing measuring errors.
    if there is no data the user is informed.

    :param: slope = k 
    :param: constant_term = b
    '''

    x_list = app_state_dictionary["x_data"]
    if not x_list:
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"], "No data selected, please import data"
        )
    else:
        for index, value in enumerate(x_list):
            y = slope * value + constant_term
            app_state_dictionary["y_data"][index] = app_state_dictionary["y_data"][index] - y


def linear_adaptation():
    '''
    If the user has clicked integrate or background remove button I.e. seen the guide message.
    
    The function collects the mouse data from last two clicks.
    Calculates the equation between these clicked points.
    Calculates the new Y-values and subtracts them from the Y-data.
    Clears the graph and plots the changed data in it's place.

    else the function directs the user to pick two datapoints.
    '''
    graph = app_state_dictionary["graph_box"]
    if app_state_dictionary["counter"] % 2 == 0:
        x_1,y_1,x_2,y_2 = prior_mouse_data() # y = slope*x + constant_term
        slope, constant_term = calculate_line_equation(x_1,y_1,x_2,y_2) 
        calculate_data_by_equation(slope, constant_term)
        graph[2].cla()
        plot_data()
    else:
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"],
            "Now click two datapoints on the graph and click 'remove background' again"
        )
        ik.kirjoita_tekstilaatikkoon(
            app_state_dictionary["text_box"],
            "Or use the last two datapoints by double-clicking 'remove background'"
        )
    app_state_dictionary["counter"] = app_state_dictionary["counter"] +1


def help_guide():
    '''
    Infroms the user about the application using the text box.
    '''
    ik.kirjoita_tekstilaatikkoon(app_state_dictionary["text_box"],
        """
        This application takes in data collectd from electron spectroscopy.
        In spectroscopy material is exposed to a bright light. This causes electrons
        to detach, by collecting this the kinetic energy of the detached electrons,
        we can understand more about the materials properties.
        After importing the data ("open folder")
        The application can display this data ("plot graph")
        Calculate the integral (surface area) between points ("Integrate")
            click "integrate" -> click two points --> click "integrate" again:
            The app will print the integral between these clicks
        Remove measuring errors using linear regression ("Remove background")
            click "Remove background" -> click two points -> click "Remove background" again:
            The app will substract values from the measurement data according to linear regression
            fitted between these points.
        You can also clear the plot and save the graph as a picture (.png)
        """
    )


def main():
    '''
    Creates a window with all the elements inside.
    Activates functions to do the required calculations.
    Links the box variables to the app_state_dictionary
    '''
    window = ik.luo_ikkuna("SpectrumAnalyzer")
    left_app_frame = ik.luo_kehys(window, ik.VASEN)
    up_app_frame = ik.luo_kehys(window, ik.YLA)
    graph = ik.luo_kuvaaja(up_app_frame, pick_datapoint, 800, 400)
    app_state_dictionary["graph_box"] = graph
    text_box = ik.luo_tekstilaatikko(up_app_frame, 99, 20)
    app_state_dictionary["text_box"] = text_box
    ik.luo_nappi(left_app_frame, "Open folder", sub_open_folder)
    ik.luo_nappi(left_app_frame, "Plot graph", plot_data)
    ik.luo_nappi(left_app_frame, "Remove background", linear_adaptation)
    ik.luo_nappi(left_app_frame, "Integrate", integrate)
    ik.luo_nappi(left_app_frame, "Save as PNG", save_as_png)
    ik.luo_nappi(left_app_frame, "Clear plot", clear_plot)
    ik.luo_nappi(left_app_frame, "Help", help_guide)
    ik.luo_nappi(left_app_frame, "Quit", ik.lopeta)
    ik.kaynnista()

main()
