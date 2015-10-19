#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  INFERENCE TEST SCRIPT   #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

print '\n------RUNNING INFERENCE TESTING------'
print '----------------------------------------\n'

## ----------------------------------------------------------------------------
# Load valid trials given the shj type
if sys.platform == 'darwin':
#   [F1, F2, F3, CATEGORY, RESPONSE_FEATURE, CORRECT, SHJ]
    inference_list = np.genfromtxt(
        os.getcwd() + '/inferencetrials.csv',
        delimiter = ',', dtype = 'int', skip_header = 1).astype(float)
else:
    inference_list= np.genfromtxt(
        os.getcwd() + '\\inferencetrials.csv',
        delimiter = ',', dtype = 'int', skip_header = 1).astype(float)

# Reduce trial listings
inference_list = inference_list[inference_list[:, -1] == shj_condition]
inference_list = inference_list[:, 0:-1]


## ----------------------------------------------------------------------------
# Define block -- based on trials listed in inferencetrials
print '-----INFERENCE TEST BLOCK:'
inference_block = []
for i in stimuli:
    stim_features = np.array(i[2])
    stim_features[np.isnan(stim_features)] = -1.0
    for j in inference_list:
        trial_features = np.array(j[0:3])
        if np.array_equal(stim_features, trial_features):
            print j
            response_feature = int(j[4]) - 1
            category = category_names[int(j[3])]
            correct = int(j[5])
            inference_block.append([i, category, response_feature, correct])


## ----------------------------------------------------------------------------
## LOAD BUTTONS, TEXT, ETC
    
# Create rectangles that subsitute for actual image buttons
click_rectangles = []
click_rectangles.append(visual.Rect(win,
    width = image_sizes[1][0], height = image_sizes[1][1], pos = [-100,-125]))
click_rectangles.append(visual.Rect(win,
    width = image_sizes[1][0], height = image_sizes[1][1], pos = [100,-125]))

## ----------------------------------------------------------------------------
# Present instructions and wait for response
phase = 'inference_test'
present_instructions(win, instructions, instruction_text, phase)


## ----------------------------------------------------------------------------
# Iterate over trials
print '\n------executing trials------\n'
rnd.shuffle(inference_block)

trial_num = 1
for trial in inference_block:

#   Define trial properites
    start_category   = trial[1]
    start_image      = trial[0][0]
    file_name        = trial[0][1]
    start_properties = trial[0][2]
    response_feature = trial[2]
    correct_response = trial[3]
    
#   Set task text and set image params
    start_image.setSize(image_sizes[0])
    start_image.setPos(image_start)
    task_text = ('Which of these would you expect for a member of the ' + 
        start_category + ' category?')
    instructions.setText(task_text)    

#   Get current buttons
    [button_images, button_labels, button_borders] = get_inference_buttons(
        stimuli, response_feature, image_sizes[1], win)

#   Draw fix cross
    start_trial(win, .5, fix_cross)

#   Draw current stimuli
    drawall(win, [start_image])
    core.wait(.5)
    drawall(win, [start_image, instructions, button_borders, button_images])
    core.wait(.5)

#   Wait for response
    [response, rt] = button_gui(cursor, timer, click_rectangles, button_labels)
    response = response[0] # ([1] is the feature #, is equal to responsefeature)

#   Combine original with response image and find the result stim
    addition = np.tile(np.nan,(1,3))[0]
    addition[response_feature] = response
    new_properties = combine_features(start_properties, addition)
    new_example_info = find_stimulus(stimuli, new_properties)

#   Update info for the generated image
    completed_image = new_example_info[0]
    completed_properties = new_example_info[2]
    
#   Draw result
    drawall(win,[completed_image])
    core.wait(.5)

#   Determine correctness
    if response == correct_response:
        accuracy = 1
    else:
        accuracy = 0

#   Update order of feature presentation
    feature_order = [0,0,0]
    feature_order[response_feature] = 1
    
#   Print trial info
    print '\nInference Test Trial ' + str(trial_num) + ' information:'
    print ['finalimage:', list(completed_properties)]
    print ['feature order:', feature_order]
    print ['queued category:', start_category]
    print ['response:', response]
    print ['correct response:', correct_response]    

#   Click to continue
    instructions.setText(continue_string)
    drawall(win,[completed_image, instructions])
    core.wait(.5)        
    click_to_continue(cursor)

#   Log data
    current_trial = [subject_number, condition, shj_condition, 
        balance_condition, phase, '', trial_num, file_name,
        list(completed_properties), feature_order, start_category, response,
        correct_response, rt, accuracy]
    subject_data.append(current_trial)
    write_file(subject_file, subject_data, ',')

    trial_num = trial_num + 1
            
