using UnityEngine;

[System.Serializable]
public class Landmark
{
    public string geom_nr;
    public string body;               // The body of the landmark (e.g., cube, ball, pyramid)
    public string color;              // The color of the landmark (e.g., red, green, blue)
    public float[] start_coordinate;  // Start coordinate of the landmark
    public float[] goal_coordinate;   // Goal coordinate of the landmark
}

[System.Serializable]
public class LandmarkData
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
    public Landmark[] landmarks;      // Array of landmarks
}
