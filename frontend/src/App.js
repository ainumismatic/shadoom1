import React, { useState, useEffect } from 'react';
import './App.css';
import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  GoogleAuthProvider, 
  signInWithPopup, 
  signOut, 
  onAuthStateChanged,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  updateProfile
} from 'firebase/auth';
import axios from 'axios';

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDrkS6uab1cSIj_ciA0EyWQ650QrEN0-Tk",
  authDomain: "shadoom-online-10716.firebaseapp.com",
  projectId: "shadoom-online-10716",
  storageBucket: "shadoom-online-10716.firebasestorage.app",
  messagingSenderId: "213287212310",
  appId: "1:213287212310:web:e6c975021fe3d996d46c37"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [topic, setTopic] = useState('');
  const [ideas, setIdeas] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showProfileAnalysis, setShowProfileAnalysis] = useState(false);
  const [profileAnalysis, setProfileAnalysis] = useState(null);
  const [analyzingProfile, setAnalyzingProfile] = useState(false);
  
  // Auth form states
  const [showLogin, setShowLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [instagramHandle, setInstagramHandle] = useState('');
  const [tiktokHandle, setTiktokHandle] = useState('');
  const [kwaiHandle, setKwaiHandle] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState('');

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          // Create or get user in our database
          const userData = {
            email: firebaseUser.email,
            name: firebaseUser.displayName || firebaseUser.email.split('@')[0] || 'Usuário',
            profile_pic: firebaseUser.photoURL || null,
            instagram_handle: instagramHandle || null,
            tiktok_handle: tiktokHandle || null,
            kwai_handle: kwaiHandle || null
          };
          
          console.log('Creating user with data:', userData); // Debug log
          
          const response = await axios.post(`${API}/users`, userData);
          setUser(response.data);
          
          // Load user's ideas history
          loadUserIdeas(response.data.id);
        } catch (error) {
          console.error('Error creating user:', error);
          console.error('Error details:', error.response?.data); // Debug log
          
          // Clear Firebase auth if backend fails
          if (error.response?.status === 422) {
            setAuthError('Erro ao criar perfil. Tente novamente.');
            await signOut(auth);
          }
        }
      } else {
        setUser(null);
        setIdeas([]);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, [instagramHandle, tiktokHandle, kwaiHandle]);

  const signInWithGoogle = async () => {
    setAuthLoading(true);
    setAuthError('');
    try {
      // Add additional domain configuration
      provider.setCustomParameters({
        prompt: 'select_account'
      });
      
      await signInWithPopup(auth, provider);
    } catch (error) {
      console.error('Login error:', error);
      console.error('Error code:', error.code); // Debug log
      
      switch (error.code) {
        case 'auth/unauthorized-domain':
          setAuthError('Domínio não autorizado. Configure o Firebase para este domínio.');
          break;
        case 'auth/popup-closed-by-user':
          setAuthError('Login cancelado pelo usuário.');
          break;
        case 'auth/popup-blocked':
          setAuthError('Popup bloqueado. Permita popups para este site.');
          break;
        default:
          setAuthError('Erro ao fazer login com Google. Tente novamente.');
      }
    } finally {
      setAuthLoading(false);
    }
  };

  const signUpWithEmail = async (e) => {
    e.preventDefault();
    if (!email || !password || !name) {
      setAuthError('Preencha todos os campos obrigatórios');
      return;
    }
    
    setAuthLoading(true);
    setAuthError('');
    
    try {
      // Create user account
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      
      // Update profile with name
      await updateProfile(userCredential.user, {
        displayName: name
      });
      
      // Clear form
      setEmail('');
      setPassword('');
      setName('');
      setInstagramHandle('');
      setTiktokHandle('');
      setKwaiHandle('');
      
    } catch (error) {
      console.error('Signup error:', error);
      switch (error.code) {
        case 'auth/email-already-in-use':
          setAuthError('Este email já está cadastrado. Tente fazer login.');
          break;
        case 'auth/weak-password':
          setAuthError('A senha deve ter pelo menos 6 caracteres.');
          break;
        case 'auth/invalid-email':
          setAuthError('Email inválido.');
          break;
        default:
          setAuthError('Erro ao criar conta. Tente novamente.');
      }
    } finally {
      setAuthLoading(false);
    }
  };

  const signInWithEmail = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setAuthError('Preencha email e senha');
      return;
    }
    
    setAuthLoading(true);
    setAuthError('');
    
    try {
      await signInWithEmailAndPassword(auth, email, password);
      
      // Clear form
      setEmail('');
      setPassword('');
      
    } catch (error) {
      console.error('Login error:', error);
      switch (error.code) {
        case 'auth/user-not-found':
        case 'auth/wrong-password':
        case 'auth/invalid-credential':
          setAuthError('Email ou senha incorretos.');
          break;
        case 'auth/too-many-requests':
          setAuthError('Muitas tentativas. Tente novamente mais tarde.');
          break;
        default:
          setAuthError('Erro ao fazer login. Tente novamente.');
      }
    } finally {
      setAuthLoading(false);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const loadUserIdeas = async (userId) => {
    try {
      const response = await axios.get(`${API}/ideas/${userId}`);
      setIdeas(response.data);
    } catch (error) {
      console.error('Error loading ideas:', error);
    }
  };

  const generateIdeas = async () => {
    if (!topic.trim() || !user) return;

    setGenerating(true);
    try {
      const response = await axios.post(`${API}/generate-ideas`, {
        user_id: user.id,
        topic: topic.trim()
      });
      
      const newIdeas = response.data;
      setIdeas(prevIdeas => [...newIdeas, ...prevIdeas]);
      setTopic('');
      
      // Update user data to reflect new ideas count
      const userResponse = await axios.get(`${API}/users/${user.email}`);
      setUser(userResponse.data);
      
    } catch (error) {
      console.error('Error generating ideas:', error);
      if (error.response?.status === 403) {
        alert('Limite de ideias atingido! Faça upgrade para Premium para ideias ilimitadas.');
      } else {
        alert('Erro ao gerar ideias. Tente novamente!');
      }
    } finally {
      setGenerating(false);
    }
  };

  const analyzeProfile = async (platform, handle) => {
    if (!user || !handle.trim()) return;
    
    setAnalyzingProfile(true);
    try {
      const response = await axios.post(`${API}/analyze-profile`, {
        user_id: user.id,
        platform: platform,
        handle: handle.trim()
      });
      
      setProfileAnalysis(response.data);
    } catch (error) {
      console.error('Error analyzing profile:', error);
      if (error.response?.status === 403) {
        alert('Análise de perfil disponível apenas para usuários Premium!');
      } else {
        alert('Erro ao analisar perfil. Tente novamente!');
      }
    } finally {
      setAnalyzingProfile(false);
    }
  };

  const upgradeToPremium = async () => {
    try {
      await axios.post(`${API}/upgrade-plan`, {
        user_id: user.id,
        plan: "premium"
      });
      
      // Update user data
      const userResponse = await axios.get(`${API}/users/${user.email}`);
      setUser(userResponse.data);
      
      alert('Upgrade para Premium realizado com sucesso! 🎉');
    } catch (error) {
      console.error('Error upgrading plan:', error);
      alert('Erro ao fazer upgrade. Tente novamente!');
    }
  };

  const deleteIdea = async (ideaId) => {
    try {
      await axios.delete(`${API}/ideas/${ideaId}`);
      setIdeas(prevIdeas => prevIdeas.filter(idea => idea.id !== ideaId));
    } catch (error) {
      console.error('Error deleting idea:', error);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copiado para área de transferência! 📋');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Carregando Shadoom...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 flex items-center justify-center p-4">
        <div className="max-w-5xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            
            {/* Left side - Branding */}
            <div className="text-center lg:text-left">
              <div className="mb-8">
                <img 
                  src="https://images.pexels.com/photos/8728386/pexels-photo-8728386.jpeg" 
                  alt="Shadoom AI Technology"
                  className="w-full h-72 object-cover rounded-2xl shadow-2xl mb-6 opacity-90"
                />
              </div>
              
              <h1 className="text-5xl lg:text-6xl font-bold text-white mb-4">
                👻 <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">Shadoom</span>
              </h1>
              <p className="text-xl text-purple-200 mb-4">
                Seu Gerenciador Fantasma de Engajamento
              </p>
              <p className="text-purple-300 max-w-lg mx-auto lg:mx-0 mb-8">
                Banco Secreto de Ideas com IA • Análise completa do seu perfil • Nunca mais fique sem conteúdo!
              </p>
              
              {/* Plans Comparison */}
              <div className="grid grid-cols-2 gap-4 text-center mb-8">
                <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
                  <h3 className="text-lg font-bold text-white mb-2">FREE</h3>
                  <ul className="text-purple-200 text-sm space-y-1">
                    <li>✅ 10 ideias/mês</li>
                    <li>✅ Roteiros básicos</li>
                    <li>❌ Análise de perfil</li>
                  </ul>
                </div>
                <div className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 backdrop-blur-lg rounded-xl p-4 border border-purple-400/30">
                  <h3 className="text-lg font-bold text-white mb-2">PREMIUM</h3>
                  <ul className="text-purple-200 text-sm space-y-1">
                    <li>✅ Ideias ilimitadas</li>
                    <li>✅ Análise IA completa</li>
                    <li>✅ Insights das redes</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Right side - Auth Form */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-white mb-2">
                  {showLogin ? 'Entrar na Shadoom' : 'Criar Conta Grátis'}
                </h2>
                <p className="text-purple-200">
                  {showLogin ? 'Bem-vindo de volta!' : 'Comece a gerar ideias agora'}
                </p>
              </div>

              {/* Error Message */}
              {authError && (
                <div className="bg-red-500/20 border border-red-500/30 text-red-200 p-3 rounded-lg mb-4 text-sm">
                  {authError}
                </div>
              )}

              {/* Email/Password Form */}
              <form onSubmit={showLogin ? signInWithEmail : signUpWithEmail} className="space-y-4 mb-6">
                {!showLogin && (
                  <>
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Seu nome completo *"
                      className="w-full px-4 py-3 rounded-lg bg-white/10 backdrop-blur-lg border border-white/20 text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-400"
                      disabled={authLoading}
                      required
                    />
                    
                    <div className="grid grid-cols-1 gap-3">
                      <input
                        type="text"
                        value={instagramHandle}
                        onChange={(e) => setInstagramHandle(e.target.value)}
                        placeholder="@instagram (opcional)"
                        className="w-full px-4 py-2 rounded-lg bg-white/10 backdrop-blur-lg border border-white/20 text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-400 text-sm"
                        disabled={authLoading}
                      />
                      <div className="grid grid-cols-2 gap-2">
                        <input
                          type="text"
                          value={tiktokHandle}
                          onChange={(e) => setTiktokHandle(e.target.value)}
                          placeholder="@tiktok"
                          className="w-full px-4 py-2 rounded-lg bg-white/10 backdrop-blur-lg border border-white/20 text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-400 text-sm"
                          disabled={authLoading}
                        />
                        <input
                          type="text"
                          value={kwaiHandle}
                          onChange={(e) => setKwaiHandle(e.target.value)}
                          placeholder="@kwai"
                          className="w-full px-4 py-2 rounded-lg bg-white/10 backdrop-blur-lg border border-white/20 text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-400 text-sm"
                          disabled={authLoading}
                        />
                      </div>
                    </div>
                  </>
                )}
                
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Seu email *"
                  className="w-full px-4 py-3 rounded-lg bg-white/10 backdrop-blur-lg border border-white/20 text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  disabled={authLoading}
                  required
                />
                
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Sua senha *"
                  className="w-full px-4 py-3 rounded-lg bg-white/10 backdrop-blur-lg border border-white/20 text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  disabled={authLoading}
                  required
                />
                
                <button
                  type="submit"
                  disabled={authLoading}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-bold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-300"
                >
                  {authLoading ? '⏳ Carregando...' : showLogin ? '🚀 Entrar' : '✨ Criar Conta'}
                </button>
              </form>

              {/* Divider */}
              <div className="relative mb-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-white/20"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-transparent text-purple-200">ou</span>
                </div>
              </div>

              {/* Google Login */}
              <button
                onClick={signInWithGoogle}
                disabled={authLoading}
                className="w-full bg-white text-gray-800 py-3 px-4 rounded-lg font-bold hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-2 mb-6"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="#4285f4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34a853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#fbbc05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#ea4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span>Entrar com Google</span>
              </button>

              {/* Toggle Form */}
              <div className="text-center">
                <button
                  onClick={() => {
                    setShowLogin(!showLogin);
                    setAuthError('');
                    setEmail('');
                    setPassword('');
                    setName('');
                    setInstagramHandle('');
                    setTiktokHandle('');
                    setKwaiHandle('');
                  }}
                  className="text-purple-300 hover:text-white transition-colors"
                >
                  {showLogin ? 'Não tem conta? Criar agora' : 'Já tem conta? Entrar'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-lg border-b border-white/20">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-white">👻 Shadoom</h1>
            <span className="text-purple-200">|</span>
            <span className="text-purple-200">
              {user.plan === 'premium' ? '✨ Premium' : '🆓 Free'} 
              {user.plan === 'free' && ` (${user.ideas_generated || 0}/10 ideias)`}
            </span>
          </div>
          
          <div className="flex items-center space-x-4">
            {user.plan === 'free' && (
              <button
                onClick={upgradeToPremium}
                className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-4 py-2 rounded-lg font-bold hover:from-yellow-600 hover:to-orange-600 transform hover:scale-105 transition-all duration-300 text-sm"
              >
                ⭐ Upgrade Premium
              </button>
            )}
            
            <button
              onClick={() => {
                setShowHistory(false);
                setShowProfileAnalysis(false);
              }}
              className={`px-4 py-2 rounded-lg transition-colors ${!showHistory && !showProfileAnalysis ? 'bg-purple-600 text-white' : 'bg-purple-600/50 text-white hover:bg-purple-600/70'}`}
            >
              ✨ Gerar Ideas
            </button>
            
            <button
              onClick={() => {
                setShowHistory(true);
                setShowProfileAnalysis(false);
              }}
              className={`px-4 py-2 rounded-lg transition-colors ${showHistory ? 'bg-purple-600 text-white' : 'bg-purple-600/50 text-white hover:bg-purple-600/70'}`}
            >
              📚 Histórico
            </button>
            
            {user.plan === 'premium' && (
              <button
                onClick={() => {
                  setShowProfileAnalysis(true);
                  setShowHistory(false);
                }}
                className={`px-4 py-2 rounded-lg transition-colors ${showProfileAnalysis ? 'bg-purple-600 text-white' : 'bg-purple-600/50 text-white hover:bg-purple-600/70'}`}
              >
                🔍 Análise Premium
              </button>
            )}
            
            <div className="flex items-center space-x-2">
              {user.profile_pic && (
                <img
                  src={user.profile_pic}
                  alt={user.name}
                  className="w-8 h-8 rounded-full"
                />
              )}
              <span className="text-white text-sm">{user.name}</span>
            </div>
            
            <button
              onClick={handleSignOut}
              className="text-purple-200 hover:text-white transition-colors"
            >
              Sair
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {showProfileAnalysis && user.plan === 'premium' ? (
          /* Profile Analysis Section */
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">
              🔍 Análise Premium de Perfil
            </h2>
            <p className="text-purple-200 mb-8">
              Análise completa das suas redes sociais com insights da IA
            </p>

            <div className="grid md:grid-cols-3 gap-4 mb-8 max-w-2xl mx-auto">
              {user.instagram_handle && (
                <button
                  onClick={() => analyzeProfile('instagram', user.instagram_handle)}
                  disabled={analyzingProfile}
                  className="bg-gradient-to-r from-pink-600 to-purple-600 text-white py-3 px-4 rounded-lg font-bold hover:from-pink-700 hover:to-purple-700 disabled:opacity-50 transform hover:scale-105 transition-all duration-300"
                >
                  📷 Analisar Instagram
                </button>
              )}
              {user.tiktok_handle && (
                <button
                  onClick={() => analyzeProfile('tiktok', user.tiktok_handle)}
                  disabled={analyzingProfile}
                  className="bg-gradient-to-r from-red-600 to-pink-600 text-white py-3 px-4 rounded-lg font-bold hover:from-red-700 hover:to-pink-700 disabled:opacity-50 transform hover:scale-105 transition-all duration-300"
                >
                  🎵 Analisar TikTok
                </button>
              )}
              {user.kwai_handle && (
                <button
                  onClick={() => analyzeProfile('kwai', user.kwai_handle)}
                  disabled={analyzingProfile}
                  className="bg-gradient-to-r from-orange-600 to-red-600 text-white py-3 px-4 rounded-lg font-bold hover:from-orange-700 hover:to-red-700 disabled:opacity-50 transform hover:scale-105 transition-all duration-300"
                >
                  ⚡ Analisar Kwai
                </button>
              )}
            </div>

            {analyzingProfile && (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">🤖</div>
                <p className="text-purple-200">Analisando seu perfil com IA...</p>
              </div>
            )}

            {profileAnalysis && (
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 max-w-4xl mx-auto">
                <h3 className="text-2xl font-bold text-white mb-6">
                  Análise: @{profileAnalysis.handle} ({profileAnalysis.platform})
                </h3>
                
                <div className="grid md:grid-cols-2 gap-8 text-left">
                  <div>
                    <h4 className="text-lg font-bold text-purple-200 mb-3">📊 Análise Geral</h4>
                    <p className="text-purple-100 mb-6">{profileAnalysis.analysis}</p>
                    
                    <h4 className="text-lg font-bold text-purple-200 mb-3">⏰ Melhores Horários</h4>
                    <div className="flex space-x-2 mb-6">
                      {profileAnalysis.best_posting_times.map((time, index) => (
                        <span key={index} className="bg-purple-600/30 text-purple-200 px-3 py-1 rounded-full text-sm">
                          {time}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-lg font-bold text-purple-200 mb-3">💡 Recomendações</h4>
                    <ul className="space-y-2 mb-6">
                      {profileAnalysis.recommendations.map((rec, index) => (
                        <li key={index} className="text-purple-100 text-sm flex items-start">
                          <span className="text-purple-400 mr-2">•</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                
                <div className="border-t border-white/20 pt-6 mt-6">
                  <div className="grid md:grid-cols-2 gap-8 text-left">
                    <div>
                      <h4 className="text-lg font-bold text-purple-200 mb-3">👥 Insights da Audiência</h4>
                      <p className="text-purple-100 text-sm">{profileAnalysis.audience_insights}</p>
                    </div>
                    <div>
                      <h4 className="text-lg font-bold text-purple-200 mb-3">📈 Performance</h4>
                      <p className="text-purple-100 text-sm">{profileAnalysis.content_performance}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : !showHistory ? (
          /* Generate Ideas Section */
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">
              🧠 Banco Secreto de Ideas
            </h2>
            <p className="text-purple-200 mb-2">
              Digite qualquer tópico e receba ideias criativas instantaneamente!
            </p>
            {user.plan === 'free' && (
              <p className="text-yellow-300 text-sm mb-8">
                Plano Free: {user.ideas_generated || 0}/10 ideias usadas este mês
              </p>
            )}

            <div className="max-w-2xl mx-auto mb-8">
              <div className="flex space-x-4">
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="Ex: ansiedade, fitness, moda, negócios, culinária..."
                  className="flex-1 px-6 py-4 rounded-full bg-white/10 backdrop-blur-lg border border-white/20 text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  onKeyPress={(e) => e.key === 'Enter' && generateIdeas()}
                />
                <button
                  onClick={generateIdeas}
                  disabled={generating || !topic.trim() || (user.plan === 'free' && user.ideas_generated >= 10)}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-full font-bold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-300"
                >
                  {generating ? '🤖 Gerando...' : '✨ Gerar Ideas'}
                </button>
              </div>
              
              {user.plan === 'free' && user.ideas_generated >= 10 && (
                <p className="text-yellow-200 text-sm mt-4">
                  Limite atingido! Faça upgrade para Premium para ideias ilimitadas 🚀
                </p>
              )}
            </div>
          </div>
        ) : (
          /* Ideas History Header */
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">
              📚 Suas Ideas Salvas
            </h2>
            <p className="text-purple-200">
              {ideas.length} ideias criativas no seu arsenal
            </p>
          </div>
        )}

        {/* Ideas Grid */}
        {ideas.length > 0 && (showHistory || (!showHistory && !showProfileAnalysis)) && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ideas.map((idea, index) => (
              <div
                key={idea.id}
                className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300 transform hover:scale-105"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <span className="bg-purple-600 text-white text-xs px-2 py-1 rounded-full">
                      {idea.content_type}
                    </span>
                    <span className="text-purple-200 text-xs">
                      {new Date(idea.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <button
                    onClick={() => deleteIdea(idea.id)}
                    className="text-red-400 hover:text-red-300 text-sm"
                  >
                    🗑️
                  </button>
                </div>
                
                <h3 className="text-white font-bold text-lg mb-3 leading-tight">
                  {idea.title}
                </h3>
                
                <div className="bg-black/20 rounded-lg p-3 mb-4">
                  <p className="text-purple-100 text-sm whitespace-pre-line">
                    {idea.script}
                  </p>
                </div>
                
                <div className="flex flex-wrap gap-1 mb-4">
                  {idea.hashtags.map((tag, tagIndex) => (
                    <span
                      key={tagIndex}
                      className="text-purple-300 text-xs bg-purple-900/30 px-2 py-1 rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => copyToClipboard(idea.title)}
                    className="flex-1 bg-purple-600/50 text-white text-xs py-2 px-3 rounded-lg hover:bg-purple-600/70 transition-colors"
                  >
                    📋 Título
                  </button>
                  <button
                    onClick={() => copyToClipboard(idea.script)}
                    className="flex-1 bg-purple-600/50 text-white text-xs py-2 px-3 rounded-lg hover:bg-purple-600/70 transition-colors"
                  >
                    📝 Roteiro
                  </button>
                  <button
                    onClick={() => copyToClipboard(idea.hashtags.join(' '))}
                    className="flex-1 bg-purple-600/50 text-white text-xs py-2 px-3 rounded-lg hover:bg-purple-600/70 transition-colors"
                  >
                    🏷️ Tags
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {ideas.length === 0 && showHistory && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">💡</div>
            <h3 className="text-2xl font-bold text-white mb-2">
              Nenhuma ideia salva ainda
            </h3>
            <p className="text-purple-200 mb-6">
              Gere suas primeiras ideias criativas para começar!
            </p>
            <button
              onClick={() => setShowHistory(false)}
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-3 rounded-full font-bold hover:from-purple-700 hover:to-pink-700 transform hover:scale-105 transition-all duration-300"
            >
              ✨ Gerar Ideas Agora
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 bg-black/20 backdrop-blur-lg border-t border-white/10">
        <div className="max-w-6xl mx-auto px-4 py-6 text-center">
          <p className="text-purple-200">
            👻 Shadoom - Seu assistente invisível para engajamento máximo
          </p>
          <p className="text-purple-300 text-sm mt-2">
            {user.plan === 'premium' ? 'Premium' : 'Free'} • Powered by Gemini AI • Análise completa de perfil
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;