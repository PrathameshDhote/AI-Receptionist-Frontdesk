import React from 'react';
import { TrendingUp, Clock, CheckCircle, XCircle } from 'lucide-react';

export default function Stats({ stats }) {
  const statCards = [
    {
      title: 'Pending',
      value: stats?.pending || 0,
      icon: Clock,
      color: 'bg-yellow-500',
      textColor: 'text-yellow-600',
    },
    {
      title: 'Resolved',
      value: stats?.resolved || 0,
      icon: CheckCircle,
      color: 'bg-green-500',
      textColor: 'text-green-600',
    },
    {
      title: 'Timeout',
      value: stats?.timeout || 0,
      icon: XCircle,
      color: 'bg-red-500',
      textColor: 'text-red-600',
    },
    {
      title: 'Total',
      value: stats?.total || 0,
      icon: TrendingUp,
      color: 'bg-blue-500',
      textColor: 'text-blue-600',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {statCards.map((stat) => {
        const Icon = stat.icon;
        return (
          <div
            key={stat.title}
            className="bg-white rounded-lg shadow-lg p-6 border-l-4"
            style={{ borderLeftColor: stat.color.replace('bg-', '#') }}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className={`text-3xl font-bold ${stat.textColor} mt-2`}>
                  {stat.value}
                </p>
              </div>
              <div className={`p-3 rounded-full ${stat.color} bg-opacity-10`}>
                <Icon className={`w-8 h-8 ${stat.textColor}`} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
