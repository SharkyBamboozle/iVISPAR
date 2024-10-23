using UnityEngine;

[System.Serializable]
public class Landmark
{
    public string body;
    public string color;
    public float[] coordinate;  
    public  float[] goal_coordinate;
}

[System.Serializable]
public class LandmarkData
{
    public string experiment_id;
    public int grid_size;
    public Landmark[] landmarks;
}

