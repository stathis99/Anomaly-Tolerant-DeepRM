import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def bi_model_dist(num_res, max_nw_size, job_len):
    num_res = num_res
    max_nw_size = max_nw_size
    job_len = job_len

    job_small_chance = 0.8

    job_len_big_lower = job_len * 2 / 3
    job_len_big_upper = job_len

    job_len_small_lower = 1
    job_len_small_upper = job_len / 5

    dominant_res_lower = max_nw_size / 2
    dominant_res_upper = max_nw_size

    other_res_lower = 1
    other_res_upper = max_nw_size / 5

    # -- job length --
    if np.random.rand() < job_small_chance:  # small job
        nw_len = np.random.randint(job_len_small_lower,
                                    job_len_small_upper + 1)
    else:  # big job
        nw_len = np.random.randint(job_len_big_lower,
                                    job_len_big_upper + 1)

    nw_size = np.zeros(num_res)

    # -- job resource request --
    dominant_res = np.random.randint(0, num_res)
    for i in range(num_res):
        if i == dominant_res:
            nw_size[i] = np.random.randint(dominant_res_lower,
                                            dominant_res_upper + 1)
        else:
            nw_size[i] = np.random.randint(other_res_lower,
                                            other_res_upper + 1)

    return nw_len, nw_size    


def log_norm_dist(num_res, max_nw_size, job_len):
    num_res = num_res

    mu_lenght = 2  
    sigma_lenght = 0.5
    mu_res = 2.5
    sigma_res = 0.4 
      
    nw_len = np.round(np.random.lognormal(mu_lenght, sigma_lenght, 1)).astype(int)


    nw_size = np.zeros(num_res)

    # -- job resource request --
    dominant_res = np.random.randint(0, num_res)
    for i in range(num_res):
        if i == dominant_res:
            nw_size[i] = np.round(np.random.lognormal(mu_res, sigma_res, 1)).astype(int)

        else:
            nw_size[i] = np.round(np.random.lognormal(mu_res, sigma_res, 1)).astype(int)

    return nw_len, nw_size    

    
def generate_sequence_work(simu_len):

    nw_len_seq = np.zeros(simu_len, dtype=int)
    nw_size_seq = np.zeros((simu_len, 2), dtype=int)

    time = np.arange(simu_len)
    arrival_rate = 0.5 + 0.5 * np.sin(2 * np.pi * time / (simu_len / 24))  



    for i in range(simu_len):

        if np.random.poisson(arrival_rate[i]+1) > 0:  # a new job comes

            nw_len_seq[i], nw_size_seq[i, :] = log_norm_dist(2,10,15)

    return nw_len_seq, nw_size_seq

def save_jobs_csv(nw_len_seq, nw_size_seq, filename="jobs_training/jobs_lognorm.csv"):

    # Combine job length and size information into a single array for easier saving
    data = np.column_stack((nw_len_seq, nw_size_seq))

    # Save the data to a CSV file with headers
    np.savetxt(filename, data, delimiter=",", header="len,res1,res2", fmt="%d")  # Assuming size has 2 dimensions




def launch_generate(train_sample):
    print("Jobs to be generated :", )
    nw_len_seqs, nw_size_seqs = generate_sequence_work(train_sample)
    # print(nw_len_seqs)
    # print(nw_size_seqs)

    save_jobs_csv(nw_len_seqs, nw_size_seqs)
    print("done !")

def launch_train():
    print("Train model!")
    train = pd.read_csv('jobs_training/jobs_lognorm.csv')
    train_normalized = (train - train.mean()) / train.std()
    
    # Initialize and train the Isolation Forest model
    isolation_forest = IsolationForest(n_estimators=100, max_samples='auto', contamination='auto', random_state=42, behaviour='new')
    isolation_forest.fit(train_normalized)
    
    # Predict outliers/anomalies
    predictions = isolation_forest.predict(train_normalized)
    # Create a DataFrame for predictions
    predictions_df = pd.DataFrame(predictions.reshape(-1, 1), columns=['Prediction'])
    
    # Concatenate the predictions DataFrame with the original DataFrame along the appropriate axis
    train_with_predictions = pd.concat([train, predictions_df], axis=1)
    
    # Save the DataFrame with predictions as a new CSV file
    train_with_predictions.to_csv('jobs_training/jobs_lognorm_with_predictions.csv', index=False)
    
    # Count anomalies
    num_anomalies = sum(predictions == -1)
    print("Number of anomalies detected:", num_anomalies)
    print("done !")

