#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  SWITCH TASK TRAINING SCRIPT   #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

print '\n--------RUNNING SWITCHIT TRAINING------'

## define training block -- based on all 3f images
print '-----TRAINING ITEMS:'
training_block       = []
switch_button_images = []
stim_feature_list    = []
item_index           = []

# Text stim for the label of the final category
final_cat_label = visual.TextStim(win, text = '', font = text_font, color= text_color,
	height = text_size, pos = [0, 0])

# Grab appropriate switch_button_images
for i in stimuli:
    features = i[2]
    num_missing_features = sum(np.isnan(features))
    if num_missing_features == 0:
        training_block.append(i)
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
for i in training_block:
    i.append(category_names[which_category(i[-1], valid_egs)])
    i.append(training_block.index(i) + 1)
    print i
    stim_feature_list.append(i[2])
    item_index.append(training_block.index(i)+1)

## make reference list for the switch matrix
stim_feature_list = [[stim_feature_list],[item_index]]

## create switch matrix
#print '-----------Switch Matrix------------'
switch_matrix = make_switch_matrix(training_block,stim_feature_list)

## present instructions and wait for response
phase = 'switch_train'
present_instructions(win, instructions, instruction_text, phase)

## __________________________________________________________
# Execute tutorial (?)                                                   |
tutorialskip = False # True to skip
if not tutorialskip:
    switch_tutorial(win, instructions, image_start,
        [[-100,-125],[100,-125],[0,-225]], text_font,
        text_color, text_size, cursor, timer, image_sizes)
## __________________________________________________________|
##

# Set the location of each button
button_locations=[[-200,-125],
                  [0,-125],
                  [200,-125],
                  [0,-275]]

# Create click areas
click_rectangles = []
for i in button_locations:
    click_rectangles.append(visual.Rect(win, width = image_sizes[1][0], 
    									height = image_sizes[1][1], pos = i))

# Edit properties for the done button
click_rectangles[-1] = visual.Rect(win, width = 150, height = 75, pos = [0,-275])


# Iterate over all training trials
print '\n------executing trials------\n'
for block_num in range(1, num_training_blocks+1):
    # Shuffle, set up counters
    rnd.shuffle(training_block)
    accuracy  = 0
    trial_num = 1
    
    # Run through each trial in the training block
    for trial in training_block:
        #keep track of inaccruate attempts on each trial
        attempt_counter = 0

        # Keep reloading same trial until participant is accurate
        while accuracy == 0:
        	
            # Define trial properites
            start_image      = trial[0]
            file_name        = trial[1]
            start_properties = trial[2]
            start_category   = trial[3]
            # Set start and target category labels
            if start_category == 'Lape':
                target_category = 'Tannet'
            else:
                target_category = 'Lape' 
            # Set start locations
            start_image.setSize(image_sizes[0])
            start_image.setPos(image_start)
        
        	# Set task text
            task_text = ('Use the buttons below to change this leaf into a ' + 
                         target_category + ' leaf.')
            instructions.setText(task_text)

        	# Grab buttons
            [button_images, button_labels, button_covers, switch_labels] = get_switch_buttons(
                stimuli, feature_names, button_locations, image_sizes[1], start_properties,
                switch_button_images, win, False, text_font, text_color, text_size)
        
        	# Draw fix cross
            start_trial(win, .5, fix_cross) 

        	# Run gui interface
            [completed_stimulus_info, button_pushed, rt] = switch_gui(win, cursor, 
            	timer, stimuli, trial, switch_labels, button_images, click_rectangles,
            	feature_names, instructions, switch_matrix, button_covers, 
                final_cat_label, target_category, phase)

        	# Get info about final example
            attempt_counter     += 1
            completed_image      = completed_stimulus_info[0]
            completed_properties = completed_stimulus_info[2]

        	# Save properties for final stimulus
            completed_properties = list(completed_properties.astype(int))
            for i in valid_egs:
                if completed_properties in i:
                    current_category = valid_egs.index(i)
                    current_category = category_names[current_category]

            # Set feedback text, set image positions | stim properties 
            if current_category == start_category:
                feedback = ('Incorrect... you made a ' + 
                    current_category + ' leaf. Try again!')
                accuracy = 0

                if current_category == 'Lape':
                    completed_image.setPos([-150,150])
                    final_cat_label.setText(start_category)
                    final_cat_label.setPos([-150,270])
                else:
                    completed_image.setPos([150,150])
                    final_cat_label.setText(start_category)
                    final_cat_label.setPos([150,270])
                    
            else:
                feedback = 'Correct! you made a ' + target_category + ' leaf.'
                final_cat_label.setText(target_category)
                accuracy = 1
                
            instructions.setText(feedback)
            drawall(win, [instructions, completed_image, final_cat_label])
            core.wait(.5)

        	# Click to continue
            instructions.setText(feedback + continue_string)
            drawall(win, [completed_image, instructions, final_cat_label])
        
        	# Log data
            current_trial = [subject_number, condition, shj_condition, 
                balance_condition, phase, block_num, trial_num,
                attempt_counter, file_name, list(completed_properties), 
                list(start_properties), start_category, current_category, rt, 
                accuracy, sum(button_pushed)]
            
            # Append to complete data and write file
            subject_data.append(current_trial)
            write_file(subject_file, subject_data,',')

            # Print trial info
            print ('Block ' + str(block_num), 'Trial ' + str(trial_num) + '-' +
                str(attempt_counter) + ' information:')
            print ['finalimage: ', list(completed_properties)]
            print ['buttons pushed: ', button_pushed]
            print ['original cat: ', start_category]
            print ['switched cat: ', current_category]
            print ['accuracy: ', accuracy]
            
            click_to_continue(cursor)

        # End trial 
        trial_num = trial_num + 1
        accuracy  = 0
        click_to_continue(cursor)

  
    # Reset image locs
    for i in training_block:
        i[0].setPos([0,150])
