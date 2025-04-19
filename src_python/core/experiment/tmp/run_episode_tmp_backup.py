async def run_episode2(self, agent, game, episode_logger=None):
    """
    Perform repeated interactions with the server after the connection has been established.
    """

    response = await self.websocket.recv()
    state = json.loads(response)
    # delay = agent.delay

    i = 0
    while not game.check_done(state):
        # log_separator(f"Action-Perception Loop: {i}", logger=episode_logger)
        # time.sleep(delay)

        # if message_data.get("command") == "Screenshot" or message_data.get("command") == "ActionAck":

        # state = game.feed_sim_response(message_data, i) #TODO replace
        action = agent.act(state)
        # game.feed_agent_response(action) #TODO replace

        # state = game.step(action)

        # Exit the loop if the user wants to close the connection
        if action.lower() == "reset":
            await self.send_reset()
            break
        elif action.lower() == "exit":
            await self.send_reset()
            await self.websocket.close()
            episode_logger.info("Connection closed")
            break
        else:
            message_data = self.send_msg(user_message=action)

        i += 1
        # game._save_logs() #TODO re-introduce

    # save last observation after game is done
    observation = game.feed_sim_response(message_data, i)
    # game._save_logs() #TODO re-introduce
    # Send the JSON message to the server
    # response = await websocket.recv()
    await self.send_reset()
    # image = game.feed_sim_response(message_data, 100)
    # game._save_logs()
    ##TODO save response data to experiment_path