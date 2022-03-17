"""
    Thomas: a program to load the model generated by train_model.py and
    continue training it for a user-specified number of epochs.

    It will use the same training, validation, and testing sets as the train_model.py script,
    provided that the lists for each have been stored in a pickle file (whose path
    is the constant DS_LABELS_PATH).
"""

import sys

from train_model import *


# Retrieve lists for training, validation, and testing sets generated by train_model.py
def retrieve_set_labels(ds_labels_path: str)\
        -> tuple[np.ndarray, tuple[np.ndarray, ...], tuple[np.ndarray, ...]]:
    with open(ds_labels_path, "rb") as pkl_fp:
        return pickle.load(pkl_fp)


def retrieve_sets(ds_labels_path: str, para2words: dict[str, str], encoder: LabelEncoder, debug: bool = False)\
        -> tuple[np.ndarray, ...]:
    train_paras, (validation_paras, test_paras), (train_targets, validation_targets,
                                                  test_targets) = retrieve_set_labels(ds_labels_path)
    
    train_files, validation_files, test_files = [], [], []
    for paragraph in train_paras:
        train_files.extend(para2words[paragraph])
    
    for paragraph in validation_paras:
        validation_files.extend(para2words[paragraph])

    for paragraph in test_paras:
        test_files.extend(para2words[paragraph])
    
    if debug:
        print(f"Train paragraphs: {len(train_paras)}")
        print(f"Train words: {len(train_files)}")
        print(f"Validation paragraphs: {len(validation_paras)}")
        print(f"Validation words: {len(validation_files)}")
        print(f"Test paragraphs: {len(test_paras)}")
        print(f"Test words: {len(test_files)}")

    train_targets, validation_targets, test_targets = np.asarray(
        train_targets), np.asarray(validation_targets), np.asarray(test_targets)
    train_targets, validation_targets, test_targets = encoder.transform(
        train_targets), encoder.transform(validation_targets), encoder.transform(test_targets)

    # Return the encoder in addition to the split dataset
    # so that it can be used by other parts of the program
    return train_files, validation_files, test_files, train_targets, validation_targets, test_targets


if __name__ == "__main__":
    n_epochs = 10
    if len(sys.argv) > 1:
        try:
            n_epochs = int(sys.argv[1])
        except ValueError:
            pass

    encoder = load_encoder(LE_SAVE_PATH)
    para2words, _ = categorize_all(PARAGRAPHS, WORDS)
    split_ds = retrieve_sets(DS_LABELS_PATH, para2words, encoder, debug=True)
    model, (train_generator, validation_generator,
            test_generator) = get_model_generators(split_ds, encoder)
    model.load_weights(SAVED_MODEL)

    model.compile(loss="categorical_crossentropy",
                  optimizer="adam", metrics=["accuracy", top_3_accuracy, top_5_accuracy])

    model.fit(train_generator, validation_data=validation_generator,
              epochs=n_epochs, steps_per_epoch=STEPS_PER_EPOCH, validation_steps=VALIDATION_STEPS, callbacks=[model_checkpoint_callback])

    model.evaluate(test_generator, steps=500)
