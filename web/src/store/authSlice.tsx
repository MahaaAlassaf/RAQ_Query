import { createSlice } from "@reduxjs/toolkit";

interface AuthState {
  isLogged: boolean;
  token: string;
  isAdmin: boolean;
}

const initialState: AuthState = {
  isLogged: false,
  token: "",
  isAdmin: false,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setLogged: (state, action) => {
      state.isLogged = action.payload;
    },
    setToken: (state, action) => {
      state.token = action.payload;
    },
    setIsAdmin: (state, action) => {
      state.isAdmin = action.payload;
    },
  },
});

export const { setLogged, setToken, setIsAdmin } = authSlice.actions;

export default authSlice.reducer;
