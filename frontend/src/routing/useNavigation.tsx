// src/hooks/useNavigation.ts
import { useAuth } from "../auth/AuthContext";
import { useNavigate } from "react-router-dom";

export const useNavigationHelpers = () => {
    const { logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            const response = await fetch('/api/users/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                logout();
                navigate('/');
            } else {
                console.error('Logout failed');
            }
        } catch (error) {
            console.error('Error logging out:', error);
        }
    };

    const handleHome = () => {
        navigate('/');
    };

    const goToDashboard = () => {
        navigate('/dashboard');
    };

    const goToFriends = () => {
        navigate('/friends');
    };

    return { handleLogout, handleHome, goToDashboard, goToFriends };
};
