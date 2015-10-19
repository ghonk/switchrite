#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  SWITCHRITE SUPPORT FUNCTIONS  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

from psychopy import visual, event, core, gui
import os, random as rnd, socket, sys, shutil, datetime
import numpy as np


# Creates folder if it doesnt exist
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def check_directory(dir): 
    if not os.path.exists(dir):
        os.makedirs(dir)


# Create text entry window and return subject info 
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def get_subject_info(experiment_name, conditions, data_location):
    ss_info = []
    pc = socket.gethostname()
    my_Dlg = gui.Dlg(title=experiment_name)
    my_Dlg.addText('Subject Info')
    my_Dlg.addField('ID:', tip='or subject code')
    my_Dlg.addField('Condition:', rnd.choice(conditions), choices = conditions)
    my_Dlg.show()
    if not my_Dlg.OK:
        print 'User Terminated'
        core.quit()
        
    subject_info = [str(i) for i in my_Dlg.data]
    
    if subject_info[0]=='':
        core.quit()
    else: 
        id = subject_info[0]
        condition = subject_info[1]
        subject_file = (data_location + pc + '-' + experiment_name + '-' + 
            condition + '-' + id + '.csv')
        while os.path.exists(subject_file) == True:
            subject_file = (data_location + pc + '-' + experiment_name + '-' + 
                condition + '-' + id + '.csv' + '_dupe')
        return [int(id),int(condition),subject_file]


# Re-assigns dimension and feature values based on counterbalance lists
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def counterbalance(subject_number, stimuli, feature_balance_list,
                    dimension_balance_list, feature_names):

    # Select a counterbalance condition based on subject
    n_conditions = len(feature_balance_list)
    condition    = subject_number % n_conditions
    
    # Balance features
    feature_assignment = feature_balance_list[condition] == 1
    print ['FLIPPED FEATURES:', feature_assignment]
    for i in stimuli:
        features = i[2]
        features[feature_assignment] = 1 - features[feature_assignment]
        stimuli[stimuli.index(i)][2] = features
    # Balance dimensions and create labels    
    dimension_assignment = dimension_balance_list[condition] - 1
    orig_feature_names   = list(feature_names)
    count = 0
    for i in dimension_assignment:
        feature_names[count] = orig_feature_names[i]
        count = count + 1
    print ['DIMENSION SHUFFLE:', dimension_assignment,feature_names]
    for i in stimuli:
        features = i[2]
        stimuli[stimuli.index(i)][2] = features[dimension_assignment]
       
    print ''
    return [stimuli, condition, feature_names, dimension_assignment]


# copies the data file to a series of dropbox folders
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def copy_2_db(file_name, experiment_name):
    copy_folders = [ #add your own!
        'C:\\Users\\klab\\Dropbox\\PSYCHOPY DATA\\' + experiment_name + '\\',
        'C:\\Users\\klab\\Dropbox\\garrett\\PSYCHOPY DATA\\' + experiment_name + '\\']

    for i in copy_folders:
        check_directory(i)
        shutil.copy(file_name,i)
        

# Flatten a list
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def flatten(LIST):
    for i in LIST:
        if isinstance(i, (list, tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i


# Converts an array into a list  
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def array_2_list(data,int_convert):
    result = np.array(data)
    result[np.isnan(result)] = -1 #convert nan to -1

    if int_convert: #convert to integer if desired
        result = result.astype(int)
        
    result = result.tolist()
    return result   


# takes in a string and return a list of integers; a=0, b=1, ... _=nan
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def str_2_prop(string):
    features = np.tile(np.nan, [1, len(string)])[0]
    for dimension in range(0,len(string)):
        character = string[dimension]
        if character != '_':
             features[dimension] = (ord(character) - ord('a'))
    return features


# Present instructions  
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def present_instructions(win, stim, text, phase):
    event.clearEvents()
    original_position = stim.pos
    stim.setPos       = [0.0,0.0]
    stim.alignVert    = 'center'
    
    # Search text for instructions matching phase
    for i in text:
        if i[0] == phase:
            instructs = i[1]
            break
            
    # Draw text and wait for key press
    stim.setText(instructs)
    stim.draw()
    win.flip()
    core.wait(2)
    if 'q' in event.waitKeys(keyList = ['q','space']):
        print 'User Terminated'
        core.quit()
    
    stim.alignVert = 'top'
    stim.setPos = original_position
    event.clearEvents() 


# draw a list of objects with any length/dimensions
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def drawall(win,objects):
    for i in objects:
        if isinstance(i, (list, tuple)):
            for j in flatten(i):
                j.draw()
        else:
            i.draw()
    win.flip()


# monitor buttons, when clicked return click result
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def button_gui(cursor, timer, buttons, labels):

    # Clear events
    timer.reset()
    cursor.clickReset()
    event.clearEvents() 
    
    # Iterate until response
    while True:
        
        # Quit if desired
        if 'q' in event.getKeys():
            print 'User Terminated'
            core.quit()
            
        # Check to see if any stimulus has been clicked on
        for i in buttons:
            if cursor.isPressedIn(i):
                return [labels[buttons.index(i)], timer.getTime()]


# Find images with a provided set of properties
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def find_stimulus(stims, comparison):
    comparison = np.array(comparison)
    comparison[np.isnan(comparison)] = -1
    for i in stims:
        features = np.array(i[2])
        features[np.isnan(features)] = -1
        if np.array_equal(features, comparison):
            return i


# Program waits for a mouse click to continue
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def click_to_continue(cursor):
    event.clearEvents()
    cursor.clickReset() 
    while cursor.getPressed()==[False,False,False]:
        cursor.getPressed()
        if event.getKeys(keyList = 'q'):
            print 'User Terminated'
            core.quit()


# Determines which category a stimulus is in 
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def which_category(features, valid_egs):

    # convert to list if necessary
    if 'list' not in str(type(features)):
        features = array_2_list(features,True)
    
    category = -1
    for i in valid_egs:
        cat_num = valid_egs.index(i)
        if features in i:
            category = cat_num
            
    return category


# Do the initial blankcreen-fixcross start to a trial
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def start_trial(win, isi, fix_cross):
    fix_cross.draw()
    win.flip()
    core.wait(isi)   


# writes list to file
def write_file(file_name, data, delim):
    data_file = open(file_name, 'w')
    for line in data: #iterate over items in data list
        current_line = '\n' #start each line with a newline
        for j in line: #add each item onto the current line

            if isinstance(j, (list, tuple)): #check if item is a list
                for k in j:
                    current_line = current_line + str(k) + delim
            else:
                current_line = current_line + str(j) + delim
                
##        write current line
        data_file.write(current_line)
    data_file.close()  


#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  Condition Specific Functions  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #


#  Switch Train Functions 
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

# takes training stims and feature list and outputs switch matrix
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def make_switch_matrix(training_block,stim_feature_list):
    
    # Set up matrix ingredients 
    feat_index = stim_feature_list[1]
    temp_feature_list = array_2_list(stim_feature_list[0][0], True)
    sf_list = array_2_list(stim_feature_list[0][0], True)

    # Zeroed switch matrix    
    switch_matrix = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],
                     [0,0,0],[0,0,0],[0,0,0],[0,0,0]]
                
    # Go through each item               
    for item in [0,1,2,3,4,5,6,7]:
        # And each feature for that item        
        for j in [0,1,2]:
            # Check value of feature and switch it
            if sf_list[item][j] == 0:
                temp_feature_list[item][j] = 1
            else:
                temp_feature_list[item][j] = 0
            # Find stimulus with features that match the switch       
            for i in sf_list:
                if i == temp_feature_list[item]:
                    switch_matrix[item][j] = feat_index[0][sf_list.index(i)]
                    # Clear out temp list and end search  
                    temp_feature_list = array_2_list(stim_feature_list[0][0], True)
                    break

    return switch_matrix

# formats switch buttons
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def get_switch_buttons(stimulus_list, feature_names, button_locations,
            button_size, trial_properties, switch_button_images, win,
            tutorial, text_font, text_color, text_size):

    # Get correct feature buttons
    if tutorial != True:    
        images = []
        for i in feature_names[0:]:
            for j in switch_button_images:
                if i == j[3] and trial_properties[feature_names.index(i)] != j[4]:
                    images.append(j)
                    break
    else:
        images = list(switch_button_images)

    # Shuffle feature images
    if tutorial != True:
        rnd.shuffle(images)
    
    # Set position and size for all images,
    # Place images and labels into dedicated lists
    button_images = []
    button_labels = []
    button_covers = []
    switch_labels = list(feature_names)
    switch_labels.append('Done')
    
    for i in images:
        image_num = images.index(i)
        # Make button border    
        border = visual.Rect(win, width = button_size[0]+2, height = button_size[1]+2)
        border.setFillColor([1,1,1])
        border.setLineColor([-1,-1,-1])
        border.setPos(button_locations[image_num])
        button_images.append(border)
        
        # Edit image and store it as a button
        i[0].setPos(button_locations[image_num])
        i[0].setSize(button_size)
        button_images.append(i[0])
        
        # Store value for the provided feature
        if tutorial != True:
            features = i[2]
            provided_feature = i[3]
            feature_value = features[np.isnan(features) == False].astype(int)
            button_labels.append([feature_value[0], provided_feature])
            switch_labels[images.index(i)] = provided_feature
        # Create button covers
        j = visual.Rect(win, width = button_size[0]+10, height = button_size[1]+10)
        j.setFillColor([1,1,1])
        j.setLineColor([1,1,1])
        j.setPos(button_locations[image_num])
        button_covers.append(j)

    # Make done button    
    p = visual.Rect(win, width = 150, height = 75)
    p.setFillColor([.9,.9,.9])
    p.setLineColor([-1,-1,-1])
    p.setPos(button_locations[-1])
    button_images.append(p)    
    a = visual.TextStim(win, 'Done', font = text_font, color = text_color, 
        height = text_size, pos = button_locations[-1])
    button_images.append(a)
    
    # Make done cover    
    j = visual.Rect(win, width = 155, height = 80)
    j.setFillColor([1,1,1])
    j.setLineColor([1,1,1])
    j.setPos(button_locations[-1])
    button_covers.append(j)    

    return [button_images, button_labels, button_covers, switch_labels]


# runs switch tutorial
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def switch_tutorial(win, instructions, image_start, button_locations,
                text_font, text_color, text_size, cursor, timer, image_sizes):

    # Initiate tutorial and temp variables    
    image_directories = [os.getcwd() + '\\tutorial\\']
    label_list = ['Eyes', 'Mouth', 'Done']
    
    # Create text objects
    enter_to_cont = visual.TextStim(win, text = 'Press the spacebar to continue',
        wrapWidth = 1000, color = text_color, font = text_font, 
        height = text_size, pos = [0,-330])
    
    tut_stim_lab = visual.TextStim(win, text = 'Target: Happy Face', wrapWidth=1000,
        color = text_color, font = text_font, height = text_size, pos = [150,335])
    
    x = visual.TextStim(win, text = 'X', wrapWidth = 1000, color = text_color,
        font = text_font, height = 100, pos = image_start)
    
    # Create remaining variables needed for tutorial
    tut_stimuli   = []
    tut_images    = []
    tut_labels    = []
    tut_covers    = []
    tut_response  = []
    tut_end       = False
    eyes_pressed  = 0
    mouth_pressed = 0

    #  Make click locations for tutorial buttons
    click_rectangles_tut = []
    for i in button_locations: # changed from [[-100,-125],[100,-125],[0,-225]]
        click_rectangles_tut.append(visual.Rect(win, width = image_sizes[1][0], 
            height = image_sizes[1][1], pos = i))

    # Adjust for tutorial images
    tut_image_start = list(image_start)
    
    for i in image_directories:
        temp = []
        for j in os.listdir(i):
            if j[j.find('.'):] in ['.jpg','.png','.jpeg']:
                tut_stimuli.append ([visual.ImageStim(win, image = i+j, name = j, 
                                                      pos = tut_image_start), j])

    # Get buttons for tutorial
    [button_images, button_labels, button_covers, switch_labels] = get_switch_buttons(
        tut_stimuli[0:4], label_list, button_locations, [120,60], [0,0,0],
        tut_stimuli[4:6], win, True, text_font, text_color, text_size)

    # Tutorial screen 1    
    instructions.setText("    At the start of each trial you will see an image"
                         " in the location above.\nThe image will be a member"
                         " of one of the categories you are learning about.")
    drawall(win, [instructions, x, enter_to_cont])
    core.wait(1)

    if 'q' in event.waitKeys(keyList=['q','space']):
        print 'User Terminated'
        core.quit()

    # Tutorial screen 2    
    instructions.setText("    For practice, let's imagine that you are learning"
                         " to categorize\nexamples of unhappy faces and happy faces.")
    
    tut_stimuli[0][0].setPos(np.array(tut_image_start) - np.array([120,0]))
    tut_stimuli[2][0].setPos(np.array(tut_image_start) + np.array([120,0]))
    drawall(win, [instructions, tut_stimuli[0][0], tut_stimuli[2][0], enter_to_cont])
    core.wait(1)
    
    if 'q' in event.waitKeys(keyList = ['q', 'space']):
        print 'User Terminated'
        core.quit()
        
    # Reset image locs    
    tut_stimuli[0][0].setPos(tut_image_start)
    tut_stimuli[2][0].setPos(tut_image_start)

    # Tutorial screen 3    
    instructions.setText("    On each trial you will use the provided buttons to"
                         " change the\nexample into a member of the requested"
                         " category (a happy face).")

    drawall(win, [instructions, tut_stimuli[0][0], button_images, button_labels, enter_to_cont])
    
    if 'q' in event.waitKeys(keyList = ['q','space']):
        print 'User Terminated'
        core.quit()

    # Tutorial screen 4        
    instructions.setText("    In this case, the target category (a happy face)" 
                         " would have\ndifferent eyes and a different mouth, so"
                         " practice clicking on\nthe buttons to make the image"
                         " fit the target category.")
    drawall(win, [instructions, tut_stimuli[0][0], button_images, button_labels])
    
    while not tut_end:
        [tut_response, tut_rt] = button_gui(cursor, timer, click_rectangles_tut,
            switch_labels)
        if 'Eyes' in tut_response:
            if mouth_pressed == 0:
                tut_stimuli[1][0].setPos([150,175])
                drawall(win, [instructions, tut_stimuli[1][0], tut_stim_lab,
                    button_images,button_labels,button_covers[0]])
                eyes_pressed = 1        
            if mouth_pressed == 1:
                tut_end = True
        if 'Mouth' in tut_response:
            if eyes_pressed == 0:
                tut_stimuli[3][0].setPos([150,175])
                drawall(win, [instructions, tut_stimuli[3][0], tut_stim_lab,
                    button_images, button_labels, button_covers[1]])
                mouth_pressed = 1
            if eyes_pressed == 1:
                tut_end = True

    # Tutorial screen 6            
    while not 'Done' in tut_response:
        tut_stimuli[2][0].setPos([150,175]) 
        instructions.setText("    When you complete your changes you will"
                             " click the done button.\nYou will then be"
                             " provided feedback about the example you created!")
        enter_to_cont.setText('Click the done button to receive feedback.')

        drawall(win,[instructions, tut_stimuli[2][0], tut_stim_lab,
            button_images, button_labels, button_covers[:2], enter_to_cont])
        tut_response = []
        core.wait(.25)
        [tut_response, tut_rt] = button_gui(cursor, timer, click_rectangles_tut, switch_labels)                    

    # Tutorial screen 7
    enter_to_cont.setText('Press the spacebar to continue')
    instructions.setText('Correct! You made a member of the "Happy Face" category.')
    tut_stim_lab.setText("Happy Face")
    drawall(win, [instructions, tut_stimuli[2][0], tut_stim_lab, enter_to_cont])
    
    if 'q' in event.waitKeys(keyList = ['q','space']):
        print 'User Terminated'
        core.quit()

    # Tutorial screen 8                
    tut_stim_lab.setPos([0,50])
    tut_stim_lab.setText("Alright! It looks like you've got the hang of it."
                       "\n\nRemember: your goal in the following task is to"
                       " learn about two new categories by making changes, just"
                       " like you practiced.\n\nAt first you will have to guess"
                       " what changes to make in order to produce a member of"
                       " the requested category.  You will receive feedback"
                       " that will help guide your learning.\n\nImportantly,"
                       " you will be tested at the end of this task to see how well"
                       " you learned the categories.\n\nPlease ask the experimenter"
                       " if you have any questions.")
    enter_to_cont.setText('Press the spacebar to begin the experiment')
    drawall(win, [tut_stim_lab, enter_to_cont])

    # Clear some variables
    buttonimages = []
    buttonlabels = []
    buttoncovers = [] 
    switchlabels = []

    if 'q' in event.waitKeys(keyList = ['q', 'space']):
        print 'User Terminated'
        core.quit()



# waits for responses and completes examples corresponding to user input
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def switch_gui(win, cursor, timer, stimulus_list, trial_info, switch_labels,
                button_images, click_rectangles, feature_names, instructions,
                switch_matrix, button_covers, cat_lab_fin, 
                target_category, phase):

    # Determine trial properites
    current_trial      = list(trial_info)
    current_image      = trial_info[0]
    current_properties = trial_info[2]

    # Initalize data to be updated in trial loop
    num_responses    = 0
    new_example_info = []
    trial_covers     = []
    end_trial        = False
    button_pushed    = [0] * len(switch_labels)
    new_properties   = list(current_properties)
        
    # Trial loop starts
    while not end_trial:
        # Draw trial for all trials > 1
        if num_responses > 0:
            instructions.setText(
                "Here is what you've done so far to make this a " + 
                target_category + ". Change another feature OR click done.")    
            drawall(win, [current_image, click_rectangles, button_images, 
                instructions, trial_covers, cat_lab_fin])
            core.wait(.25)
        # Draw first trial
        else:
            drawall(win, [current_image, click_rectangles, button_images, 
                instructions, button_covers[-1]])
            core.wait(.25)
        # Get response 
        [response, rt] = button_gui(cursor, timer, click_rectangles, switch_labels)                
        print response
        # Continue trial as function of response
        for i in switch_labels:
            # Populate list with pushed buttons  
            if i in response and button_pushed[switch_labels.index(i)] != 1:
                button_pushed[switch_labels.index(i)] = 1
                print button_pushed
                button_pushed[-1] = 0
                
                # Find out if a feature button is pressed (vs done)    
                if switch_labels.index(i) <= len(switch_labels) - 2:
                    # Change target feature and find matching example
                    if current_properties[feature_names.index(response)] == 0.0:
                        new_properties[feature_names.index(response)] = 1.0
                    else:
                        new_properties[feature_names.index(response)] = 0.0
                    new_example_info = find_stimulus(stimulus_list, new_properties)
                    # Set new properties
                    current_image = new_example_info[0]
                    current_properties = list(new_properties)
                    cat_lab_fin.setPos([0,270])
                    if trial_info[3] == 'Tannet':
                        cat_lab_fin.setText('Target: Lape')
                        if phase == 'switch_train':    
                            current_image.setPos([-150,150])
                            cat_lab_fin.setPos([-150,270])
                    else:
                        cat_lab_fin.setText('Target: Tannet')
                        if phase == 'switch_train':    
                            current_image.setPos([150,150])
                            cat_lab_fin.setPos([150,270])
                            
                    trial_covers.append(button_covers[switch_labels.index(i)])
                    num_responses = num_responses + 1
                    
                elif i == switch_labels[-1]:
                    if num_responses > 0:
                        num_responses = num_responses + 1
                        end_trial = True
                    else:
                        num_responses = 0

    return [new_example_info, button_pushed, rt]


#  Classify Train Functions 
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

# runs switchit tutorial
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def classify_tutorial(win, instructions, image_start, buttons, button_text,
    text_font, text_color, text_size, cursor, timer, image_sizes):
    
    # Initialize tutorial vars    
    image_directories = [os.getcwd() + '\\tutorial\\']
    enter_to_cont = visual.TextStim(win, text = 'Press the spacebar to continue',
        wrapWidth = 1000, color = text_color, font = text_font, 
        height = text_size, pos = [0, -330])
    x = visual.TextStim(win, text = 'X', wrapWidth = 1000, color = text_color,
        font = text_font, height = 100, pos = image_start)
    final_instructs = visual.TextStim(win, text = '', wrapWidth = 1000,
        color = text_color, font = text_font, height = text_size, pos = ([0,50]))
    
    label_list = ['Unhappy', 'Happy']
    button_text[0].setText('Unhappy')
    button_text[1].setText('Happy')
    
    # Grab tutorial stimuli    
    tut_stimuli  = []
    tut_response = []
    tut_rt       =[]
    
    for i in image_directories:
        temp = []
        for j in os.listdir(i):
            if j[j.find('.'):] in ['.jpg','.png','.jpeg']:
                tut_stimuli.append ([
                    visual.ImageStim(win, image = i + j, name = j, 
                       pos = image_start), j])

    # Tutorial screen 1    
    instructions.setText("    At the start of each trial you will see an image"
        " in the location above.\nThe image will be a member of one of the"
        " categories you are learning about.")
    drawall(win,[instructions, x, enter_to_cont])
    core.wait(1)
    if 'q' in event.waitKeys(keyList = ['q','space']):
        print 'User Terminated'
        core.quit()
    
    # Tutorial screen 2    
    instructions.setText("    For practice, let's imagine that you are learning"
        " to categorize\n examples of unhappy faces and happy faces.")
    tut_stimuli[0][0].setPos(np.array(image_start) - np.array([120,0]))
    tut_stimuli[2][0].setPos(np.array(image_start) + np.array([120,0]))
    drawall(win,[instructions, tut_stimuli[0][0], tut_stimuli[2][0], 
        enter_to_cont])
    core.wait(1)
    
    if 'q' in event.waitKeys(keyList = ['q','space']):
        print 'User Terminated'
        core.quit()
    
    tut_stimuli[0][0].setPos(image_start)
    tut_stimuli[2][0].setPos(image_start)

    # Tutorial screen 3    
    instructions.setText("    On each trial you will use the mouse to click on"
        " the\ncategory name of the provided example.")
    drawall(win, [instructions, tut_stimuli[0][0], buttons, button_text,
        enter_to_cont])
    if 'q' in event.waitKeys(keyList = ['q','space']):
        print 'User Terminated'
        core.quit()

    #Tutorial screen 4    
    instructions.setText("    You will be provided feedback about your answer."
        "\nGo ahead and click the correct category name.")
    drawall(win, [instructions, tut_stimuli[0][0], buttons, button_text])
    
    while not 'Unhappy' in tut_response:
        [tut_response, tut_rt] = button_gui(cursor, timer, buttons, label_list)
        
        if 'Unhappy' in tut_response:
            instructions.setText(
                "Correct! This is a member of the Unhappy category")
        if 'Happy' in tut_response:
            instructions.setText(
                "Incorrect... This is a member of the Unhappy category")
            break
        
    # Tutorial screen 5    
    drawall(win, [instructions, tut_stimuli[0][0], enter_to_cont])
    if 'q' in event.waitKeys(keyList = ['q','space']):
        print 'User Terminated'
        core.quit()        

    # Tutorial screen 6    
    final_instructs.setText(
        "Alright! It looks like you've got the hang of it.\n\nRemember: your"
        " goal in the following task is to learn about two new categories by"
        " choosing the category name, just like you practiced.\n\nAt first you"
        " will have to guess the category.  You will receive feedback that will"
        " help guide your learning.\n\nImportantly, you will be tested at the"
        " end of this task to see how well you learned the categories.\n\nPlease"
        " ask the experimenter if you have any further questions.")
    drawall(win, [final_instructs, enter_to_cont])
    if 'q' in event.waitKeys(keyList = ['q','space']):
        print 'User Terminated'
        core.quit()     

    button_text[0].setText('Lape')
    button_text[1].setText('Tannet')
    

#  Inference Test Functions 
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

# Finds and formats inference images for use as buttons
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def get_inference_buttons(stims, missing_feature, button_size, win):

    # Find the appropriate stimuli
    images = []
    for i in stims:
        features = i[2]
        num_missing_features = sum(np.isnan(features))
        if (num_missing_features == 2) and (not np.isnan(features[missing_feature])):
            images.append(i)
    rnd.shuffle(images) # do a quick shuffle

    # Set image position and size
    images[0][0].setPos([-100,-125])
    images[0][0].setSize(button_size)
    images[1][0].setPos([ 100,-125])
    images[1][0].setSize(button_size)

    button_images  = []
    button_labels  = []
    button_borders = []
    
    for i in images:  
        # Store image stimulus
        button_images.append(i[0])
        # Store value for the provided feature
        features = i[2]
        feature_value = features[np.isnan(features) == False].astype(int)
        button_labels.append([feature_value[0], missing_feature])
    
    # Make border    
    border = visual.Rect(win, width = button_size[0]+2, height = button_size[1]+2)
    border.setFillColor([1,1,1])
    border.setLineColor([-1,-1,-1])
    border.setPos([-100,-125])
    button_borders.append(border)  
    border = visual.Rect(win, width = button_size[0]+2, height = button_size[1]+2)
    border.setFillColor([1,1,1])
    border.setLineColor([-1,-1,-1])
    border.setPos([100,-125])
    button_borders.append(border)
    
    
    return [button_images, button_labels, button_borders]


# Finds approprtiate inference images
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def combine_features(original, addition):
    new_properties = np.array(original)
    current_feature = 0
    for i in new_properties:
        if np.isnan(i):
            new_properties[current_feature] = addition[current_feature]
        current_feature = current_feature + 1
    return new_properties


#  Inference Test Functions 
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

#  Classify Test Functions 
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

