#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  SWITCHTEST SCRIPT #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

print '\n--------RUNNING SWITCHIT TEST------'

# Define testing block -- based on all 3f images
print '-----TEST ITEMS:'
switch_test_block = []

# Initialize trial vars
switch_button_images = []
stim_feature_list = []
item_index = []
final_cat_label = visual.TextStim(win,'',font = text_font,
    color = text_color, height = text_size, pos = [0, 0])
           
# Grab appropriate stimuli
for i in stimuli:
    features = i[2]
    num_missing_features = sum(np.isnan(features))
    if num_missing_features == 0:
        switch_test_block.append(i)
    if num_missing_features == 2:
        switch_button_images.append(i)

# Setup button image list
for i in switch_button_images:
    # Get feature label    
    feature_loc = np.where(np.isnan(i[2]) == False)
    feature_loc = feature_loc[0]
    i.append(feature_names[feature_loc])
    # Get feature value
    i.append(i[2][feature_loc])

# Combine image list with category names and index
for i in switch_test_block:
    if condition < 4:
        i.append(category_names[which_category(i[-1], valid_egs)])
        i.append(switch_test_block.index(i) + 1)
    print i
    stim_feature_list.append(i[2])
    item_index.append(switch_test_block.index(i) + 1)#\ <- fuck is this?

# Make reference list for the switch matrix
stim_feature_list = [[stim_feature_list], [item_index]]

# Create switch matrix
#print '-----------Switch Matrix------------'
switch_matrix = make_switch_matrix(switch_test_block, stim_feature_list)

# Present instructions and wait for response
phase = 'switch_test'
present_instructions(win, instructions, instruction_text, phase)
 
# Set the location of each button
button_locations = [[-200,-125],
                    [0,-125],
                    [200,-125],
                    [0,-275]]

# Initialize click areas
click_rectangles = []
for i in button_locations:
    click_rectangles.append(visual.Rect(win, width = image_sizes[1][0],
        height = image_sizes[1][1], pos = i))
# Special properties for done button (not an image)
click_rectangles[-1] = visual.Rect(win, width = 150, height = 75, pos = [0,-275])

# Iterate over blocks and trials
print '\n------executing trials------\n'
print switch_test_block
rnd.shuffle(switch_test_block)
trial_num = 1
  
for trial in switch_test_block:
    # Define trial properites
    start_image      = trial[0]
    file_name        = trial[1]
    start_properties = trial[2]
    start_category   = trial[3]
    if start_category == 'Lape':
        target_category = 'Tannet'
    else:
        target_category = 'Lape' 
    start_image.setSize(image_sizes[0])
    start_image.setPos(image_start)

    # Set task text
    task_text = ('Use the buttons below to change this leaf into a ' + 
        target_category + ' leaf.')
    instructions.setText(task_text)

    # Grab buttons
    [button_images, button_labels, button_covers, switch_labels] = (
        get_switch_buttons(stimuli, feature_names, button_locations,
            image_sizes[1], start_properties, switch_button_images, win,
            False, text_font, text_color, text_size))

    # Draw fix cross
    start_trial(win, .5, fix_cross) 

    # Run gui interface
    [completed_stimulus_info, button_pushed, rt] = switch_gui(
        win, cursor, timer, stimuli, trial, switch_labels, button_images,
        click_rectangles, feature_names, instructions, switch_matrix, 
        button_covers, final_cat_label, target_category, phase)

    #Get info about final example
    completed_image = completed_stimulus_info[0]
    completed_properties = completed_stimulus_info[2]

    # Determine correctness, block accuracy and return feedback
    completed_properties = list(completed_properties.astype(int))
    for i in valid_egs:
        if completed_properties in i:
            current_category = valid_egs.index(i)
            current_category = category_names[current_category]

    if current_category == start_category:
        accuracy = 0    
    else:
        accuracy = 1
        
    # Click to continue
    instructions.setText(continue_string)
    drawall(win, [completed_image, instructions])
    
    # Log data
    current_trial = [subject_number, condition, shj_condition, 
        balance_condition, phase, block_num, trial_num, file_name, 
        list(completed_properties), list(start_properties), start_category, 
        current_category, rt, accuracy, sum(button_pushed)]
    subject_data.append(current_trial)
    write_file(subject_file, subject_data, ',')

    # Print trial info
    print 'Block '+ str(block_num) + ', Trial ' + str(trial_num) + ' information:'
    print ['finalimage:', list(completed_properties)]
    print ['buttons pushed:', button_pushed]
    print ['original cat:', start_category]
    print ['switched cat:', current_category]
    print ['accuracy:', accuracy]

    # End trial
    core.wait(.5)        
    click_to_continue(cursor)
    trial_num = trial_num + 1
