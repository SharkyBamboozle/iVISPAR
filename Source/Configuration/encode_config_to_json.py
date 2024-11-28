def convert_to_landmarks(init_state, goal_state, geoms):
    # Prepare the landmarks list
    landmarks = []
    for geom_nr, (start, goal, (body, color)) in enumerate(zip(init_state, goal_state, geoms), start=1):
        landmark = {
            "geom_nr": geom_nr,
            "body": body,
            "color": color,
            "start_coordinate": [int(x) for x in start],  # Convert each element to native Python int             #try np.array([[1, 0], [2, 1]], dtype=np.int32).tolist()
            "goal_coordinate": [int(x) for x in goal]  # Convert each element to native Python int
        }
        landmarks.append(landmark)

    # Return the JSON structure
    return landmarks