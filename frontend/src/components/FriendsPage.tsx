import React, {useEffect, useState} from 'react';
import '../css/FriendsPage.css';
import { useNavigationHelpers } from '../routing/useNavigation';




type User = {
    id: number;
    name: string;
};

type APIUserResponse = {
    user_id: number;
    username: string;
}

function getCookie(name: string): string {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop()?.split(';')[0] ?? "";
    }
    return "";
}


const FriendsPage: React.FC = () => {
    const [allUsers, setAllUsers] = useState<User[]>([]);
    const [friends, setFriends] = useState<User[]>([]);
    const { handleLogout, handleHome, goToDashboard} = useNavigationHelpers();


    useEffect(() => {
        const fetchAllUsers = async () => {
            try {
                const response = await fetch('/api/users/retrieve');
                const data = await response.json();
                const transformed = data.results.map((u: APIUserResponse) => ({
                    id: u.user_id,
                    name: u.username
                }));
                setAllUsers(transformed);
            } catch (error) {
                console.error('Failed to fetch users:', error);
            }
        }
        const fetchFriends = async () => {
            try {
                const response = await fetch('/api/users/friends');
                const data = await response.json();
                const transformed = data.results.map((u: APIUserResponse) => ({
                    id: u.user_id,
                    name: u.username
                }));
                setFriends(transformed);
            } catch (error) {
                console.error('Failed to fetch friends:', error);
            }
        };
        fetchAllUsers();
        fetchFriends();
    }, []);

    const modifyFriend = async (user: User, action: 'add' | 'remove') => {
        try {
            const response = await fetch(`/api/users/friends/${user.name}`, {
                method: action === 'add' ? 'POST' : 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': getCookie('csrf_access_token')
                },
            });

            if (!response.ok) {
                throw new Error(`Failed to ${action} friend`);
            }

            // Re-fetch updated friends list
            const updated = await fetch('/api/users/friends');
            const data = await updated.json();
            const transformed = data.results.map((u: APIUserResponse) => ({
                id: u.user_id,
                name: u.username
            }));
            setFriends(transformed);
        } catch (error) {
            console.error(error);
        }
    };

    const isFriend = (user: User) => friends.some(f => f.id === user.id);

    return (
        <div className="friends-page-container" style={{width: '100%', height: '100%'}}>
            <header className="top-bar">
                <button
                    onClick={handleLogout}
                    className="login-button"
                    style={{
                        position: 'absolute',
                        right: '20px', // Changed from left to right
                        top: '20px',
                        padding: '10px 20px',
                        backgroundColor: '#4CAF50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer'
                    }}
                >
                    Log Out
                </button>
                <button
                    onClick={goToDashboard}
                    className="login-button"
                    style={{
                        position: 'absolute',
                        right: '125px', // Changed from left to right
                        top: '20px',
                        padding: '10px 20px',
                        backgroundColor: '#4CAF50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer'
                    }}
                >
                    Dashboard
                </button>
                <h1 className="top-bar-title">Friends View</h1>
                <button
                    onClick={handleHome}
                    className="login-button"
                    style={{
                        position: 'absolute',
                        left: '20px', // Changed from left to right
                        top: '20px',
                        padding: '10px 20px',
                        backgroundColor: 'white',
                        color: 'black',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer'
                    }}
                >
                    Home
                </button>
            </header>

            <section className="friends-section">
                <h2 className="section-title">All Users</h2>
                <div className="friends-grid" style={{width: '500px', height: '100%'}}>
                    {allUsers.map(user => (
                        <div key={user.id} className="friend-card">
                            <p className="friend-name">{user.name}</p>
                            <button
                                className="add-friend-button"
                                onClick={() => modifyFriend(user, "add")}
                                disabled={isFriend(user)}
                            >
                                {isFriend(user) ? 'Added' : 'Add Friend'}
                            </button>
                        </div>
                    ))}
                </div>
            </section>

            <section className="friends-section">
                <h2 className="section-title">Your Friends</h2>
                <div className="friends-grid" style={{width: '500px', height: '100%'}}>
                    {friends.length === 0 ? (
                        <p className="no-friends">You have no friends yet.</p>
                    ) : (
                        friends.map(friend => (
                            <div key={friend.id} className="friend-card friend-added">
                                <p className="friend-name">{friend.name}</p>
                                <button onClick={() => modifyFriend(friend, 'remove')}>Remove</button>
                            </div>
                        ))
                    )}
                </div>
            </section>
        </div>
    );
};

export default FriendsPage;
