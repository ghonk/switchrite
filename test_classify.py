#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  CLASSIFY TEST SCRIPT #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

print '\n------RUNNING CLASSIFICATION TESTING------'
print '------------------------------------\n'


phase = 'classify_test'
trial_list = '\\classifytrials.csv'
    
## ----------------------------------------------------------------------------
# Load valid trials given the shj type
if sys.platform == 'darwin':
#   [f1,f2,f3,category,shj_type]
    classify_list = np.genfromtxt(
        os.getcwd() + '/classifytrials.csv',
        delimiter = ',', dtype = 'int', skip_header = 1).astype(float)
else:
    classify_list = np.genfromtxt(
        os.getcwd() + trial_list,
        delimiter = ',', dtype = 'int', skip_header = 1).astype(float)

# Reduce trial listings
classify_list = classify_list[classify_list[:, -1] == shj_condition]
classify_features = classify_list[:, 0:3].tolist()
classify_category = classify_list[:, 3].tolist()

## ----------------------------------------------------------------
# Define classify test block -- based on the classify_list
print '-----TEST BLOCK ITEMS:'
classify_test_block = []

for i in stimuli:
    features = np.array(i[2])
    features[np.isnan(features)] = -1.0
    features = features.tolist()
    if features in classify_features:
        category = classify_category[classify_features.index(features)]
        classify_test_block.append([i, category])
for i in classify_test_block:
    print i

# Make classification buttons
buttons = []
button_text = []
for i in category_names:
    button_num = category_names.index(i)
    buttons.append(visual.Rect(win, width = 150, height = 75))
    buttons[button_num].setFillColor([.8,.8,.8])
    buttons[button_num].setLineColor([-1,-1,-1])
    buttons[button_num].setPos([-100,-100])
    if button_num == 1:
        buttons[button_num].setPos([100,-100])   
    # Create a text label
    button_text.append(visual.TextStim(win,
        text = category_names[button_num], height = text_size,font = text_font,
        color = text_color, pos = buttons[button_num].pos))


# Present instructions and wait for response
present_instructions(win, instructions, instruction_text, phase)

# Iterate over blocks and trials
print '------executing trials------\n'

rnd.shuffle(classify_test_block)
trial_num = 1

for trial in classify_test_block:        

    # Define trial properites
    image = trial[0][0]
    file_name = trial[0][1]
    properties = list(trial[0][2])
    category = int(trial[1])
    if category!=-1:
        category = category_names[category]
    else:
        category = 'nan'
    
    print category
    # Set task text
    task_text = 'Click a button to select the correct category.'
    instructions.setText(task_text)

    # Reset image size and position
    image.setSize(image_sizes[0])
    image.setPos(image_start)
    
    # Draw fix cross
    start_trial(win, .5, fix_cross)        

    # Draw current stimuli
    drawall(win, [image])
    core.wait(.5)
    drawall(win, [image, instructions, buttons, button_text])
    core.wait(.5)
            
    # Wait for response
    [response,rt] = button_gui(cursor, timer, buttons, category_names)
    drawall(win,[])
    core.wait(.5)

    # Check correctness 
    if category == 'nan': # if there is no correct answer
        accuracy = 'nan'
    else:
        if response == category:
            accuracy = 1
        else:
            accuracy = 0
    
    # Print trial info
    print 'Classify Test Trial ' + str(trial_num) + ' information:'
    print ['presented image:', properties]
    print ['actual:', category]
    print ['response:', response]
    print ['accuracy:', accuracy]
    
    # Click to continue
    
    instructions.setText(continue_string)
    drawall(win,[])
    core.wait(.5)


    # Log data
    current_trial = [subject_number, condition, shj_condition, 
        balance_condition, phase, '', trial_num, file_name,
        list(properties), '', '', '', category, response, rt, accuracy]

    subject_data.append(current_trial)
    write_file(subject_file, subject_data, ',')

    trial_num = trial_num + 1
