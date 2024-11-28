using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public class DataPacket
{
    public string command; 
    public string from;
    public string to;
    public List<string> messages;
    [NonSerialized]
    public byte[] data;

    // This property handles Base64 encoding/decoding for JSON serialization
    [SerializeField]
    public string payload;

    public DataPacket()
    {
        this.command = "";
        this.from = "";
        this.to = "";
        this.messages = new List<string>();
        
    }
    public void PrepareForSerialization()
    {
        if(data == null)
            data = Convert.FromBase64String("null");
        else
            payload = Convert.ToBase64String(data);
    }

    // Call this after deserializing
    public void LoadFromSerialized()
    {
        
        data = Convert.FromBase64String(payload);
    }
}
