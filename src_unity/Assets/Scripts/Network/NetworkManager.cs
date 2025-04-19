using System.Collections;
using System.Collections.Generic;
using Unity.Collections;
using UnityEngine;
using System.Runtime.InteropServices;
using NativeWebSocket;

using TMPro;
using System.Data.Common;
public class NetworkManger : MonoBehaviour
{
    // Start is called before the first frame update
    public static NetworkManger Instance { get; private set; }
    
    public const string server_id = "0000-0000-0000-0000";
    string network_id;
    private string partner_id;
    private WebSocket websocket;

       
    [DllImport("__Internal")]
    private static extern void CopyToClipboard(string text);
    void Awake()
    {
        // Singleton pattern
        if (Instance != null && Instance != this) 
        { 
            Destroy(this); 
        } 
        else 
        { 
            Instance = this; 
            DontDestroyOnLoad(gameObject);  // Persist this object across scenes
        }    
    }
    void Start()
    {
        EventHandler.Instance.RegisterEvent("Handshake", HandShake);
        EventHandler.Instance.RegisterEvent("Echo", EchoDump);
        EventHandler.Instance.RegisterEvent("Ack", ResponseAck);
             
    }
    public async void ConnectToServer(string serverAddress)
    {   
        Debug.Log("Attemping to connect to : " + serverAddress);
        websocket = new WebSocket(serverAddress);
        websocket.OnOpen += () =>
        {
            ExperimentManager.Instance.isConnected = true;
            Debug.Log("Connection established!");
        };

        websocket.OnError += (e) =>
        {
            Debug.Log("Error! " + e);
        };

        websocket.OnClose += (e) =>
        {
            ExperimentManager.Instance.isConnected = false;
            Debug.Log("Connection closed!");
        };

        websocket.OnMessage += (bytes) =>
        {
           DecodeNetworkData(bytes);
            
        };
        //InvokeRepeating("ServerEcho", 5f, 10f);
        await websocket.Connect();

    }
    private void DecodeNetworkData(byte[] data)
    {
        Debug.Log("recieved message from server");
        var JsonString = System.Text.Encoding.UTF8.GetString(data);
        DataPacket decodedData = JsonUtility.FromJson<DataPacket>(JsonString);
        decodedData.LoadFromSerialized();
        Debug.Log(decodedData.command);
        Debug.Log(decodedData);
        EventHandler.Instance.InvokeCommand(decodedData.command, decodedData);       
        
        // var message = System.Text.Encoding.UTF8.GetString(bytes);
    }
    public void ResponseAck(DataPacket data)
    {
        data.PrepareForSerialization();
        SendWebSocketMessage(JsonUtility.ToJson(data));
    }
    private void ServerEcho()
    {
        DataPacket data = new DataPacket();
        data.command = "Echo";
        data.to = network_id;
        data.from = network_id;
        data.messages = new List<string>();
        data.PrepareForSerialization();
        SendWebSocketMessage(JsonUtility.ToJson(data));
        //await websocket.SendText(JsonUtility.ToJson(data));
        
    }
    private void CloseConnectionGracfully()
    {
        DataPacket data = new DataPacket();
        data.command = "ClientClose";
        data.to = server_id;
        data.from = network_id;
        data.messages = new List<string>();
        data.PrepareForSerialization();
        SendWebSocketMessage(JsonUtility.ToJson(data));

        
    }
    // Update is called once per frame
    void Update()
    {
        #if !UNITY_WEBGL || UNITY_EDITOR
        if(!ExperimentManager.Instance.humanExperiment)
            websocket.DispatchMessageQueue();
        #endif
    }
    public async void SendWebSocketMessage(string data)
    {
        
        if (websocket.State == WebSocketState.Open)
        {
        // Sending bytes
        //await websocket.Send(new byte[] { 10, 20, 30 });

        // Sending plain text
            Debug.Log("sending back the data");
            Debug.Log(data);
            await websocket.SendText(data);
        }
    }
    public async void SendWebSocketMessage(byte[] data)
    {
        
        if (websocket.State == WebSocketState.Open)
        {
        // Sending bytes
        //await websocket.Send(new byte[] { 10, 20, 30 });

        // Sending plain text
            await websocket.Send(data);
        }
    }

    private async void OnApplicationQuit()
    {
        if(!ExperimentManager.Instance.humanExperiment)
        {
            CloseConnectionGracfully();
        await websocket.Close();
        }
        
    }
    
    public void HandShake(DataPacket data)
    {
        DataPacket response = new DataPacket();
        response.PrepareForSerialization();
        response.command = "ACK";
        if(data.from != server_id)
        {
            partner_id = data.from;
            Debug.LogFormat("Patner ID = {0}", partner_id);
            
            response.to =  partner_id;
            
        }
        else
        {
            network_id = data.to;
            Debug.LogFormat("registered network ID = {0}", network_id);
            response.to = server_id;
            CopyIdToClipboard();
            GameObject obj = GameObject.FindWithTag("inputField");
            if(obj != null)
                obj.GetComponent<TMP_InputField>().text = network_id;
        }
        response.from = network_id;
        response.messages = new List<string>{"Handshake Acknowledged!"};
        ResponseAck(response);
        
    }
    public DataPacket PackData(string command, List<string> messages, byte[] payload)
    {
        DataPacket data = new DataPacket();
        data.from = network_id;
        data.to = partner_id;
        data.command = command;
        data.messages = messages;
        data.data = payload;
        data.PrepareForSerialization();
        return data;

    }
    public void EchoDump(DataPacket data)
    {
        Debug.Log("command : " + data.command);
    }
    public void CopyIdToClipboard()
    {
        #if UNITY_WEBGL && !UNITY_EDITOR
            CopyToClipboard(network_id); // Call the JS function when running in WebGL
        #else
        GUIUtility.systemCopyBuffer = network_id;
        #endif
        
    }
    
}
