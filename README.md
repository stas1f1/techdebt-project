# Techdebt project for python function names

A project that utilizes fine-tuning of CodeBERT and CodeT5 to detect bad function naming in python code and suggest improvements.

## Data

Both models were trained on dataset of [code data from github](https://huggingface.co/datasets/codeparrot/github-code), from which only python files were extracted.
File data was [processed](https://github.com/stas1f1/techdebt-project/blob/main/code_data.ipynb) with ast library, utilizing syntax tree to extract function definition and body nodes outside and inside classes.

For simplicity, in-class functions (like \_\_getitem\_\_) were ignored, as well as functions with decorators. For training, the functions that do not fit in 512 token window when tokenized by RoBERTa's BPE tokenizer were omitted.

First 100k functions of the resulting dataset were used to train and validate both models, with 80/20 train/test split.

## Scorer model

RoBERTa-based [CodeBERT by Microsoft](https://huggingface.co/microsoft/codebert-base) was chosen for fine-tuning for the function name quality scorer objective. While it would be logical to formulate the task in NSP format, with input like [name]\<SEP\>[code] with token_type_ids, RoBERTa-based models are not pre-trained for the NSP task, thus do not account for token types. Therefore, the task was formulated as sequence classification with corresponding head used on model and input having the same format as suggested earlier, except for using RoBERTa's \<\/s\> separator counterpart and omitting token types altogether.

Training data was split in two halves, with the first one labelled 0 (correct class) and the latter one getting fuction names replaced with random, non-coinciding permutation of names from the entire dataset and labelled 1 (incorrect class).

codebert-base checkpoint was fine-tuned on 80k python functions for 5 epochs. Model was [trained](https://github.com/stas1f1/techdebt-project/blob/main/scorer/scorer_training.ipynb) for 3,5 hours on Tesla V100 GPU and able to reach 0.96 F1-score on validation dataset.

<p align="center">
  <img src="https://github.com/stas1f1/techdebt-project/blob/main/images/codeBert_training_loss.png" width="400" title="hover text">
  <img src="https://github.com/stas1f1/techdebt-project/blob/main/images/codeBert_validation_loss.png" width="445" title="hover text">
  <img src="https://github.com/stas1f1/techdebt-project/blob/main/images/codeBert_validation_f1.png" width="450" title="hover text">
</p>

Model [was able](https://github.com/stas1f1/techdebt-project/blob/main/scorer/scorer_testing.ipynb) to easily detect all of the correct and shuffled function names in simple  test example of real-life [code file](https://github.com/stas1f1/techdebt-project/blob/main/code_sample/code_sample_halfmashed.py).

When given the task of detecting function names with few (1-3) typos in them across large corpus, the model did not perform as good with only 0.66 accuracy across both classes (balanced).

## Generator model

T5-based [CodeT5-base for Code Summarization by Salesforce](https://huggingface.co/Salesforce/codet5-base-multi-sum) was chosen for fine-tuning for the function name generator objective. The original checkpoint is trained for summarizing code in natural language, so the hypothesis posed was that generating function name is a neighboring task, thus will be easily learned by the model. Conditional Generation head was used with arguments followed by code body definition as input and function name as target, both finished with a separator token.

codet5-base-multi-sum checkpoint was fine-tuned on 80k python functions for 2 epochs. Model was [trained](https://github.com/stas1f1/techdebt-project/blob/main/generator/generator_training.ipynb) for 9,5 hours on Tesla V100 GPU.

<p align="center">
  <img src="https://github.com/stas1f1/techdebt-project/blob/main/images/t5_training_loss.png" width="400" title="hover text">
  <img src="https://github.com/stas1f1/techdebt-project/blob/main/images/t5_validation_loss.png" width="400" title="hover text">
</p>

Generator model [was able to](https://github.com/stas1f1/techdebt-project/blob/main/generator/generator_testing.ipynb) understand simple algorithmic functions like prime number check and fibonacci sequence, however did not do so well in determining exact geometry task or the function being visualized through pyplot.

Below are example tables for random functions taken from the initial dataset's part, which was not used in training. They were separately sampled by short, medium and long-length names.

### Short-length function regeneration examples

|   | **functionName** |                         **functionGeneratedName** |                                  **functionCode** |
|--:|-----------------:|--------------------------------------------------:|--------------------------------------------------:|
| 0 |        ParseSpec |                                    GetConformance |    (traces, folder, args):\n duplicate_names =... |
| 1 |   test_fail_once | test__try_send_splunk_max_attempts_and_hex_max... |    (self):\n self.config['splunk_max_attempts'... |
| 2 |     encode_field |                                      encode_field |    (self, field, value):\n return ('{encoded}'... |
| 3 |             main |                                              main |    ():\n argument_spec = dict(group=dict(requi... |
| 4 |      set_shuffle |                                       set_shuffle |    (self, shuffle):\n 'Enable/disable shuffle ... |
| 5 |      InferError7 |                                     yield_error_7 |       (a, out):\n\n @instance\n def logic():\n... |
| 6 |     \_\_init\_\_ |                                         set_ports | (self, repo_manager_exe, server_port=0, direct... |
| 7 |         on_close |                                          on_close |    (self):\n print('Listen.on_close', os.getpi... |
| 8 |      _get_normal |                                         getNormal |           (self, pts):\n '\n Get normal vector... |
| 9 |      sys_wrapper |                         _setup_sriov_capabilities | (sriovs, vnic_capable=True, vnic_failover_capa... |

### Medium-length function regeneration examples


|   |             **functionName** |    **functionGeneratedName** |                                  **functionCode** |
|--:|-----------------------------:|-----------------------------:|--------------------------------------------------:|
| 0 |            get_positive_axis |              _normalize_axis | (axis, ndims, axis_name='axis', ndims_name='nd... |
| 1 | test_logarithmic_small_scale | test_logarithmic_small_range |    ():\n 'Test logarithmic with a small range ... |
| 2 |      update_data_module_name |      update_data_module_name |       (cr, models, old_name, new_name):\n '\n ... |
| 3 |            create_dockerfile |     create_random_dockerfile |       (repository, tag):\n '\n Creates a Docke... |
| 4 |     test_user_id_trumps_user |          test_user_id_setter |    (self):\n self.request.headers['X_USER_ID']... |
| 5 |              clone_get_equiv |                      writeme |    (self, check_integrity=True):\n 'WRITEME'\n... |
| 6 |          _verify_controllers |    _verify_bridge_col_target |    (self, ovsrec_bridge):\n ovsrec_bridge.veri... |
| 7 |          generate_auth_token |                get_signature |    (self, expiration=600):\n from app import a... |
| 8 | test_key_from_legacy_urlsafe |     test_from_legacy_urlsafe |    ():\n from google.cloud.datastore.key impor... |
| 9 |            test_destroy_node |            test_destroy_node | (self):\n status = self.driver.destroy_node...    |

### Long-length function regeneration examples

|   |                                  **functionCode** |                         **functionGeneratedName** |                                  **functionCode** |
|--:|--------------------------------------------------:|--------------------------------------------------:|--------------------------------------------------:|
| 0 |      test_wait_for_drive_state_transition_timeout |      test_wait_for_drive_state_transition_timeout |    (self):\n drive = self.driver.ex_list_user_... |
| 1 |                                     test_bad_name |           test_post_name_pattern_none_returns_400 |    (self):\n response = self.client.PxST('/for... |
| 2 |                submit_rescore_problem_for_student |                 submit_rescore_one_student_answer | (self, instructor, problem_url_name, student, ... |
| 3 |                              test_encode_utf8_eol |          test_encode_one_line_eol_after_non_ascii |    (self):\n self._test_encode('helloυ\n'.enco... |
| 4 |                        testExpandMultipleSegments |             testSegmentsMultipleStartOverlapAllow |                  (self):\n '\n Using start\n T... |
| 5 | test_header_with_maxlinelen_and_thus_should_be... | test_multiple_splittable_leading_char_followed... |       (self):\n eq = self.ndiffAssertEqual\n h... |
| 6 |                           testIgnoreMissingStrand |                   testStrandsMissingAsNegativeEnd |           (self):\n '\n Using strand, at end. ... |
| 7 |                       test_header_continuation_ws |                test_splitting_multiple_long_lines |       (self):\n eq = self.ndiffAssertEqual\n h... |
| 8 |                 test_message_from_string_boundary |   test_rfc2231_no_language_or_charset_in_boundary |    (self):\n m = 'Content-Type: multipart/alte... |
| 9 |        testGenerateFeatureSplitCandidatesInactive |        testGenerateFeatureSplitCandidatesInactive |    (self):\n with self.cached_session() as ses... |
