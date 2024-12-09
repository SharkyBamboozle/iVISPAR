using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class MenuManager : MonoBehaviour
{
    public TextMeshPro message;
    public GameObject inputField;
    private bool experimentDone = false;
    void Update()
    {
        if(ExperimentManager.Instance.humanExperiment && !experimentDone)
        {
            EventHandler.Instance.RegisterEvent("EndExperiment",ExperimentEndMessage);
            message.text = "Please press start to begin the experiment";
            inputField.SetActive(false);
        }
    }

    public void ExperimentEndMessage()
    {
        experimentDone = true;
        message.text = "You have finished the experiment!";
    }
    private void OnDestroy()
     {
        EventHandler.Instance.UnregisterEvent("EndExperiment",ExperimentEndMessage);
    }
}
