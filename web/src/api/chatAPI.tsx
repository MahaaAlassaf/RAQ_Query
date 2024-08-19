
import axiosInstance from "./config";
import { ChatResponse } from "./interfaces";

export const sendMessage = async (query: string): Promise<ChatResponse> => {
  try {
    const response = await axiosInstance.get<ChatResponse>("/chat", {
      params: {
        query: query,
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to send message: ${(error as Error).message}`);
  }
};
