import React, { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { 
  PaperAirplaneIcon,
  UserIcon,
  CpuChipIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';
import { Card, Button, LoadingSpinner } from '../components/ui';
import { api } from '../services/api';

const Message = ({ message, isUser, timestamp }) => {
  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex gap-3 max-w-3xl ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-blue-600' : 'bg-gray-200'
        }`}>
          {isUser ? (
            <UserIcon className="w-4 h-4 text-white" />
          ) : (
            <CpuChipIcon className="w-4 h-4 text-gray-600" />
          )}
        </div>
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`rounded-lg px-4 py-2 max-w-none ${
            isUser 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-900 border border-gray-200'
          }`}>
            <p className="text-sm whitespace-pre-wrap">{message}</p>
          </div>
          {timestamp && (
            <span className="text-xs text-gray-500 mt-1">
              {new Date(timestamp).toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

const AgentCard = ({ agent, isActive, onClick }) => {
  const icons = {
    fitness_coach: '🏋️',
    nutritionist: '🥗',
    program_designer: '📋',
    client_advisor: '👥',
  };

  return (
    <button
      onClick={() => onClick(agent)}
      className={`w-full text-left p-4 rounded-lg border transition-colors ${
        isActive 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
      }`}
    >
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icons[agent.type] || '🤖'}</span>
        <div className="flex-1">
          <h3 className="font-medium text-gray-900">{agent.name}</h3>
          <p className="text-sm text-gray-600">{agent.description}</p>
        </div>
      </div>
    </button>
  );
};

const QuickAction = ({ title, description, onClick }) => (
  <button
    onClick={onClick}
    className="text-left p-3 rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-colors"
  >
    <h4 className="font-medium text-gray-900 text-sm">{title}</h4>
    <p className="text-xs text-gray-600 mt-1">{description}</p>
  </button>
);

const AgentChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedAgent, setSelectedAgent] = useState(null);
  const messagesEndRef = useRef(null);

  const agents = [
    {
      id: 'fitness_coach',
      name: 'Fitness Coach',
      type: 'fitness_coach',
      description: 'Personalized workout plans and exercise guidance'
    },
    {
      id: 'nutritionist',
      name: 'Nutrition Expert',
      type: 'nutritionist', 
      description: 'Diet plans and nutritional advice'
    },
    {
      id: 'program_designer',
      name: 'Program Designer',
      type: 'program_designer',
      description: 'Custom fitness program creation'
    },
    {
      id: 'client_advisor',
      name: 'Client Advisor',
      type: 'client_advisor',
      description: 'Client management and consultation'
    }
  ];

  const quickActions = [
    {
      title: 'Create Workout Plan',
      description: 'Generate a personalized workout routine',
      message: 'Can you create a beginner-friendly workout plan for strength training?'
    },
    {
      title: 'Nutrition Advice',
      description: 'Get dietary recommendations',
      message: 'What are some healthy meal prep ideas for muscle building?'
    },
    {
      title: 'Client Assessment',
      description: 'Evaluate client fitness level',
      message: 'How should I assess a new client\'s fitness level and goals?'
    },
    {
      title: 'Program Modification',
      description: 'Adjust existing programs',
      message: 'How can I modify a workout program for someone with knee issues?'
    }
  ];

  const chatMutation = useMutation({
    mutationFn: async ({ message, agentType }) => {
      const response = await api.post('/agent/chat', {
        message,
        agent_type: agentType || 'fitness_coach',
      });
      return response.data;
    },
    onSuccess: (data) => {
      setMessages(prev => [...prev, {
        message: data.response || data.message || 'I received your message.',
        isUser: false,
        timestamp: new Date().toISOString(),
        agent: selectedAgent?.name || 'Agent'
      }]);
    },
    onError: (error) => {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        message: 'Sorry, I encountered an error processing your request. Please try again.',
        isUser: false,
        timestamp: new Date().toISOString(),
        agent: 'System',
        isError: true
      }]);
    }
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (!selectedAgent && agents.length > 0) {
      setSelectedAgent(agents[0]);
    }
  }, []);

  const handleSendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim() || !selectedAgent) return;

    const userMessage = {
      message: messageText,
      isUser: true,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    chatMutation.mutate({
      message: messageText,
      agentType: selectedAgent.type
    });
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickAction = (action) => {
    handleSendMessage(action.message);
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Agent Chat</h1>
          <p className="mt-1 text-sm text-gray-600">
            Chat with specialized fitness AI agents for personalized guidance
          </p>
        </div>
        {messages.length > 0 && (
          <Button variant="outline" onClick={clearChat}>
            Clear Chat
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Agent Selection Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          <Card className="p-4">
            <h3 className="font-medium text-gray-900 mb-3">Choose an Agent</h3>
            <div className="space-y-2">
              {agents.map((agent) => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  isActive={selectedAgent?.id === agent.id}
                  onClick={setSelectedAgent}
                />
              ))}
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="font-medium text-gray-900 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              {quickActions.map((action, index) => (
                <QuickAction
                  key={index}
                  title={action.title}
                  description={action.description}
                  onClick={() => handleQuickAction(action)}
                />
              ))}
            </div>
          </Card>
        </div>

        {/* Chat Interface */}
        <div className="lg:col-span-3">
          <Card className="flex flex-col h-[600px]">
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <CpuChipIcon className="w-4 h-4 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">
                    {selectedAgent?.name || 'Select an Agent'}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {selectedAgent?.description || 'Choose an AI agent to start chatting'}
                  </p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <CpuChipIcon className="w-12 h-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Start a conversation
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Ask your AI agent for fitness advice, workout plans, or nutrition guidance.
                  </p>
                  <p className="text-sm text-gray-500">
                    Try: "Create a beginner workout plan" or use the quick actions on the left.
                  </p>
                </div>
              ) : (
                <>
                  {messages.map((msg, index) => (
                    <Message
                      key={index}
                      message={msg.message}
                      isUser={msg.isUser}
                      timestamp={msg.timestamp}
                    />
                  ))}
                  {chatMutation.isPending && (
                    <div className="flex gap-3 justify-start mb-4">
                      <div className="flex gap-3 max-w-3xl">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                          <CpuChipIcon className="w-4 h-4 text-gray-600" />
                        </div>
                        <div className="bg-gray-100 border border-gray-200 rounded-lg px-4 py-2">
                          <LoadingSpinner size="sm" className="mr-2" />
                          <span className="text-sm text-gray-600">Thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex gap-2">
                <div className="flex-1">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={
                      selectedAgent 
                        ? "Ask me anything about fitness, nutrition, or training..." 
                        : "Select an agent to start chatting..."
                    }
                    className="w-full resize-none rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    rows={1}
                    disabled={!selectedAgent || chatMutation.isPending}
                  />
                </div>
                <Button
                  onClick={() => handleSendMessage()}
                  disabled={!inputMessage.trim() || !selectedAgent || chatMutation.isPending}
                  className="px-3 py-2"
                >
                  {chatMutation.isPending ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <PaperAirplaneIcon className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AgentChat;
