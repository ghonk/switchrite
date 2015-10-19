#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  CLASSIFY TRAINING SCRIPT   #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

print '\n------RUNNING CLASSIFICATION------'
print '------------------------------------\n'

## define classify block -- based on all full images
print '-----TRAINING ITEMS:'
training_block = []

for i in stimuli:
    features = i[2]
    num_missing_features = sum(np.isnan(features))
    if num_missing_features == 0:
        print i
        training_block.append(i)

# Make classification buttons
buttons     = []
button_text = []

for i in category_names:
    button_num = category_names.index(i)
    
    buttons.append(visual.Rect(win, width = 150, height = 75))
    buttons[button_num].setFillColor([.8, .8, .8])
    buttons[button_num].setLineColor([-1, -1, -1])
    
    buttons[button_num].setPos([-100, -100])
    if button_num == 1:
        buttons[button_num].setPos([100, -100])
        
    # Create a text label
    button_text.append(visual.TextStim(win, text = category_names[button_num],
        height = text_size, font = text_font, color = text_color, 
        pos = buttons[button_num].pos))

# Present instructions and wait for response
phase = 'classify_train'
present_instructions(win, instructions, instruction_text, phase)

## ____________________________________________________________
# TUTORIAL HERE                                                |
tutorial_skip = False
if not tutorial_skip:
    classify_tutorial(win, instructions, image_start,
        buttons, button_text, text_font, text_color, text_size,
        cursor, timer, image_sizes)
## _____________________________________________________________|



# Iterate over blocks and trials
print '------executing trials------\n'
for block_num in range(1, num_training_blocks + 1):
    rnd.shuffle(training_block)
    accuracy  = 0
    trial_num = 1
    
    for trial in training_block:
        #keep track of inaccruate attempts on each trial
        attempt_counter = 0

        while accuracy == 0:
            # Define trial properites
            image      = trial[0]
            file_name  = trial[1]
            properties = list(trial[2].astype(int))
            
            # Determine category membership
            for i in valid_egs:
                if list(properties) in i:
                    category = category_names[valid_egs.index(i)]
            
            # Set task text
            task_text = 'Click a button to select the correct category.'
            instructions.setText(task_text)

            # Draw fix cross
            start_trial(win, .5, fix_cross)        

            # Draw current stimuli
            drawall(win, [image])
            drawall(win, [image, instructions, buttons, button_text])
            core.wait(.5)
                    
            # Run gui interface
            [response, rt] = button_gui(cursor, timer, buttons, category_names)
            drawall(win, [image])
            core.wait(.5)

            # Check correctness and return feedback
            attempt_counter += 1
            if response == category:
                feedback = (
                    'Correct! this is a ' + category + ' leaf.')
                accuracy = 1
            else:
                feedback = (
                    'Incorrect... please try again!')
                accuracy = 0
            
            instructions.setText(feedback)
            drawall(win,[instructions, image])
            core.wait(.5)

            # Click to continue
            instructions.setText(feedback + continue_string)
            drawall(win, [image, instructions])

            # Log data
            current_trial = [subject_number, condition, shj_condition, 
                balance_condition, phase, block_num, trial_num, attempt_counter,
                file_name, list(properties), '', '', '', category, response, rt,
                accuracy]
            
            # Append to complete data and write file
            subject_data.append(current_trial)
            write_file(subject_file, subject_data, ',')

            # Print trial info
            print ('Block ' + str(block_num) + ' Trial ' + str(trial_num) + 
                '-' + str(attempt_counter) + ' information:')
            print ['presented image:', properties]
            print ['actual:', category]
            print ['response:', response]
            print ['accuracy:', accuracy]

            click_to_continue(cursor)

        #End Trial
        trial_num = trial_num + 1
        accuracy = 0
        click_to_continue(cursor)