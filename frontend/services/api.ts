import axios, { AxiosError } from "axios";
import { DashboardData } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Configure axios defaults
axios.defaults.timeout = 10000; // 10 seconds timeout

// Create a custom logger
const logger = {
  error: (message: string, error?: any) => {
    console.error(`[API Error] ${message}`, error);
  },
  info: (message: string, data?: any) => {
    console.info(`[API Info] ${message}`, data);
  }
};

export async function getDashboardData(): Promise<DashboardData> {
  const endpoint = `${API_BASE_URL}/api/dashboard`;
  logger.info(`Fetching dashboard data from ${endpoint}`);
  
  try {
    const response = await axios.get<DashboardData>(endpoint);
    logger.info(`Successfully fetched dashboard data`, { timestamp: new Date().toISOString() });
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    
    if (axiosError.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      logger.error(`Server responded with error ${axiosError.response.status}`, {
        status: axiosError.response.status,
        data: axiosError.response.data,
        headers: axiosError.response.headers
      });
      throw new Error(`Server error: ${axiosError.response.status} - ${JSON.stringify(axiosError.response.data)}`);
    } else if (axiosError.request) {
      // The request was made but no response was received
      logger.error("No response received from server", { request: axiosError.request });
      throw new Error("No response from server. Please check if the backend is running.");
    } else {
      // Something happened in setting up the request that triggered an Error
      logger.error("Error setting up request", { message: axiosError.message });
      throw new Error(`Request setup error: ${axiosError.message}`);
    }
  }
}

export async function getResortData(resortId: string): Promise<any> {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/resorts/${resortId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching data for resort ${resortId}:`, error);
    throw new Error(`Failed to fetch data for resort ${resortId}`);
  }
} 