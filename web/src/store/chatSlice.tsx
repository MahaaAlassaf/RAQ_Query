import { createSlice } from "@reduxjs/toolkit";
import { sendMessage } from "../api/chatAPI";

interface ChatState {
  response: string;
  responseList: string[];
  loading: boolean;
  error: string | null;
}

const initialState: ChatState = {
  response: "",
  responseList: [],
  loading: false,
  error: null,
};

export const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    clearResponse: (state) => {
      state.response = "";
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action: { payload: string }) => {
      state.error = action.payload;
    },
  },
});

export const { clearResponse, setLoading, setError } = chatSlice.actions;

export const sendChatMessageAsync =
  (params: string) =>
  async (
    dispatch: (arg0: {
      payload: any;
      type: "chat/clearResponse" | "chat/setLoading" | "chat/setError";
    }) => void
  ) => {
    dispatch(setLoading(true));
    try {
      const response = await sendMessage(params);
      dispatch(setLoading(false));
      dispatch(clearResponse());
      return response.response;
    } catch (error) {
      dispatch(setLoading(false));
      if (error instanceof Error) {
        dispatch(setError(error.message));
      } else {
        dispatch(setError("An unknown error occurred"));
      }
    }
  };

export default chatSlice.reducer;