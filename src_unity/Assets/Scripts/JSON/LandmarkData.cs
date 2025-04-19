using UnityEngine;

[System.Serializable]
public class BoardData
{
    public string geom_nr;
    public string body;               // The body of the landmark (e.g., cube, ball, pyramid)
    public string color;              // The color of the landmark (e.g., red, green, blue)
    public State start_state;  // Start coordinate of the landmark
    public State goal_state;   // Goal coordinate of the landmark
}

[System.Serializable]
public class State
{
    public int x_coordinate;
    public int z_coordinate;
    public int orientation;
    public int on_board;
}

[System.Serializable]
public class ExperimentData
{
    public string experiment_id; 
    public string experiment_type;
    
    public int grid_size;             // Size of the grid (grid_size x grid_size)
    public bool use_rendering;
    public bool auto_done_check;
    public string grid_label;
    public float[] camera_offset;
    public float[] camera_auto_override;
    public float screenshot_alpha;
    public BoardData[] board_data;      // Array of landmarks
}
