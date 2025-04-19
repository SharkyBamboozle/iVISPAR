using UnityEngine;

[System.Serializable]
public class ObjectData
{
    public string body;              
    public string color;              
    public float[] current_coordinate;  
    public float[] goal_coordinate;  

    public int current_orientation;
    public int goal_orienation;
    public int current_on_board;
    public int goal_on_board;
}
