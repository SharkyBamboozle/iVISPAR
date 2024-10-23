using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net.Sockets;
using System.Net;
using System.Threading;
using System.Text;
using System;
using UnityEngine.Events;
using System.Linq;
using GameLogic;  // Add this at the top of Server.cs

[System.Serializable]
public class PlayerMoveEvent : UnityEvent<int,string>
{

}

[System.Serializable]
public class PlayerJumpEvent : UnityEvent
{
}

public class Server:MonoBehaviour 
{
   TcpListener server = null;
   TcpClient client = null;
   NetworkStream stream = null;
   Thread thread;
   //public TargetBehaviour targetBehaviour;
   private PlayerMoveEvent playerMoveEvent;
   private PlayerJumpEvent playerJumpEvent;
   public int socketPort = 1984;

   public Camera screenshotCamera;
   //public RenderTexture topDownCameraView; not used anymore
   private Queue<System.Action> CommandQueue = new Queue<System.Action>();
   private Queue<byte[]> screenshotQueue = new Queue<byte[]>();
    private GoalChecker goalChecker;  // Add reference to GoalChecker

   private void Start()
   {
        goalChecker = new GoalChecker();  // Instantiate the GoalChecker

        if (playerMoveEvent == null)
            playerMoveEvent = new PlayerMoveEvent();
        if (playerJumpEvent == null)
            playerJumpEvent = new PlayerJumpEvent();

        GameObject[] commandables = GameObject.FindGameObjectsWithTag("Commandable");

        if(commandables.Length != 0)
        {
            foreach(GameObject commandable in commandables)
            {
                TargetBehaviour targetBehaviour = commandable.GetComponent<TargetBehaviour>();
                if(targetBehaviour != null)
                {
                    playerMoveEvent.AddListener(targetBehaviour.MovePlayer);
                    playerJumpEvent.AddListener(targetBehaviour.JumpPlayer);
                }
            }

        }
   
        thread = new Thread(new ThreadStart(SetupServer));
        thread.Start();
        
   }
   private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            SendMessageToClient("end");
        }
        if (Input.GetKeyDown(KeyCode.R))
        {
            stream.Close();
            client.Close();
            server.Stop();
            thread.Abort();
            thread = new Thread(new ThreadStart(SetupServer));
            thread.Start();
        }
        lock(CommandQueue)
        {
            //if(CommandQueue.Count != 0)
            //    Debug.LogWarning("command queue length = " + CommandQueue.Count.ToString() );
            while( CommandQueue.Count > 0)
            {
                // NOT A TYPO: first paren pair is "get the action," second is "invoke it"
                Debug.Log("Dequeuung Screenshot");
                CommandQueue.Dequeue()();
            }
        }
    }

    private void SetupServer()
    {
        try
        {
            IPAddress localAddr = IPAddress.Parse("127.0.0.1");
            server = new TcpListener(localAddr, socketPort);
            server.Start();

            byte[] buffer = new byte[100 * 1024 * 1024]; //  *1 Mbyte
            string data = null;

            while (true)
            {
                Debug.Log("Waiting for connection...");
                client = server.AcceptTcpClient();
                Debug.Log("Connected!");

                
                
                data = null;
                stream = client.GetStream();

                // Queue the screenshot generation to the main thread
                lock (CommandQueue)
                {
                    CommandQueue.Enqueue(() =>
                    {
                        Debug.Log("processing init, generate init screenshot");
                        GenerateScreenshot(); // Now this will be called from the main thread
                    });
                }
                while(screenshotQueue.Count == 0)
                {

                }
                sendScreenShot(screenshotQueue.Dequeue());

                int i;

                // reading from client
                while ((i = stream.Read(buffer, 0, buffer.Length)) != 0)
                {

                    
                    data = Encoding.UTF8.GetString(buffer, 0, i);
                    if(data == "close")
                        client.Close();
                    else
                    {
                        Debug.Log("Received: " + data.ToString());
                        lock(CommandQueue)
                        {
                            CommandQueue.Enqueue( () => {
                                List<string> command = data.ToString().Split(" ").ToList();

                                if(command[0] == "start")
                                {
                                    Debug.Log("processing command Queue: " +command[0]);
                                    Jump();
                                    //GenerateScreenshot();
                                }

                                if(command[0] == "done")
                                {
                                    Debug.Log("processing command Queue: " + command[0]);
                                    // Check if all objects have reached their goals
                                    
                                    bool isDone = goalChecker.CheckAllObjects();
                                    //#if UNITY_EDITOR
                                    //    UnityEditor.EditorApplication.isPlaying = false;
                                    //#else
                                    //    Application.Quit();
                                    //#endif
                                    if (isDone)
                                    {
                                        Debug.Log("All objects have reached their goals!");
                                        client.Close();  // Close the client connection if done
                                    }
                                    else
                                    {
                                        Debug.Log("Not all objects are at their goals yet.");
                                    }
                                }
                                
                                if(command.Count == 4)
                                {   
                                    Debug.Log("processing command Queue: " +data.ToString());
                                    int id = Animator.StringToHash(command[1] + " " + command[2]);
                                    Move(id, command[3]);
                                }

                                else
                                    Debug.Log("processing command Queue (error): " +data.ToString());
                                    Move(0,"error");
                                    //GenerateScreenshot();

                                GenerateScreenshot();
                            });
                            
                        }
                        
                        while(screenshotQueue.Count == 0)
                        {

                        }
                        sendScreenShot(screenshotQueue.Dequeue());
                    }
                }
                
            }
        }
        catch (SocketException e)
        {
            Debug.Log("SocketException: " + e);
        }
        finally
        {
            server.Stop();
        }
    }

    

    private void Move(int ID, string direction)
    {
        Debug.Log("moving");
        //Debug.LogWarning("Move command issued");
        //Debug.LogWarning("Direction is " + direction);
        playerMoveEvent.Invoke(ID,direction);
    }

    private void Jump()
    {
        Debug.Log("jumping");
        // Corrected to invoke the jump event with 3 arguments
        playerJumpEvent.Invoke();
    }

    private void OnApplicationQuit()
    {
        try
        {
        stream.Close();
        client.Close();
        server.Stop();
        }
        catch(Exception e)
        {
            Debug.Log("Connection already closed");
        }
        thread.Abort();
    }
    public void sendScreenShot(byte[] image) {
        stream.Write(image, 0, image.Length);
        Debug.Log("Screenshot sent");
    }

    public void SendMessageToClient(string message)
    {
        byte[] msg = Encoding.UTF8.GetBytes(message);
        stream.Write(msg, 0, msg.Length);
        Debug.Log("Sent: " + message);
    }

    public void GenerateScreenshot()
    {
        //Debug.LogWarning("Generate screenshot invoked!");
        StartCoroutine("RecordFrameFromTexture");
    }
    
    // use screen shot functionality
    IEnumerator RecordFrame()
    {
        yield return new WaitForEndOfFrame();
        var texture = ScreenCapture.CaptureScreenshotAsTexture();
        byte[] screenshot = texture.GetRawTextureData();
        Debug.LogWarning("Texture size is " + texture.width.ToString() + " * " + texture.height.ToString() + " with total size of " + screenshot.Length + " bytes");
        screenshotQueue.Enqueue(screenshot);
        Debug.LogWarning("screenshot queue size = " + screenshotQueue.Count.ToString());
        UnityEngine.Object.Destroy(texture);
        yield return null;
    }

    //uses render texture mechanism
    IEnumerator RecordFrameFromTexture()
    {
        yield return new WaitForEndOfFrame();
        Rect rect = new Rect(0, 0, screenshotCamera.pixelWidth, screenshotCamera.pixelHeight);
        RenderTexture renderTexture = new RenderTexture(screenshotCamera.pixelWidth, screenshotCamera.pixelHeight, 24);
        Texture2D texture = new Texture2D(screenshotCamera.pixelWidth, screenshotCamera.pixelHeight, TextureFormat.RGBA32, false);
        screenshotCamera.targetTexture = renderTexture;
        screenshotCamera.Render();
        RenderTexture.active = renderTexture;
        texture.ReadPixels(rect, 0, 0);
        texture.Apply();
        screenshotCamera.Render();
        byte[] screenshot = texture.GetRawTextureData();
        Debug.LogWarning("Texture size is " + texture.width.ToString() + " * " + texture.height.ToString() + " with total size of " + screenshot.Length + " bytes");
        screenshotQueue.Enqueue(screenshot);
        Debug.LogWarning("screenshot queue size = " + screenshotQueue.Count.ToString());
        UnityEngine.Object.Destroy(texture);
        yield return null;
    }

}
