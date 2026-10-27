import time
from score_db import save_score, get_high_scores, display_formatted_scores

def track_score(username, maze_size, mode="Solo"):
    """Track the score for a user and save it to the database."""
    start_time = time.time()
    
    # Simulate maze completion (replace this with actual maze completion logic)
    time.sleep(2)  # Simulating the time taken to complete the maze

    completion_time = int(time.time() - start_time)
    save_score(username, completion_time, maze_size, mode)

def display_top_scores(limit=10):
    """Display the top scores."""
    scores = get_high_scores(limit)
    display_formatted_scores(scores)

def main(username):
    """Main function to run the score tracking process."""
    maze_size = int(input("Enter maze size: "))

    track_score(username, maze_size)
    print("\nTop Scores:")
    display_top_scores()

if __name__ == "__main__":
    username = input("Enter your username: ")
    main(username)