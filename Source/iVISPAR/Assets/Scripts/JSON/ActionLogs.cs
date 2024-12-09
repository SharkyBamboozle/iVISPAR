using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
[System.Serializable]
public class EventLogs 
{
    public List<NetAction> Actions;
    public List<string> board_state;

    public List<ObjectData> board_data;
    public bool game_done;

    public EventLogs()
    {
        Actions = new List<NetAction>();
        board_state = new List<string>();
        board_data = new List<ObjectData>();
        game_done = false;
    }
}

[System.Serializable]
public class NetAction 
{
    public int command_count;
    public int action_count;
    public string prompt;
    public List<string> valididy;

    public NetAction()
    {
        command_count = 0;
        action_count = 0;
        prompt = "";
        valididy = new List<string>();
    }
}