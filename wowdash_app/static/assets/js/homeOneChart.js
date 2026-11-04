// Common chart configuration and utilities
const chartUtils = {
    // Common chart options
    getBaseChartOptions: (height = 264) => ({
          chart: {
            height: height,
            toolbar: { show: false },
            zoom: { enabled: false },
              dropShadow: {
                  enabled: true,
                  top: 6,
                  left: 0,
                  blur: 4,
                  color: "#000",
                  opacity: 0.1,
              },
          },
        dataLabels: { enabled: false },
          grid: {
              row: {
                  colors: ['transparent', 'transparent'],
                  opacity: 0.5
              },
              borderColor: '#D1D5DB',
              strokeDashArray: 3,
          },
          xaxis: {
            categories: [],
            tooltip: { enabled: false },
            labels: { style: { fontSize: "14px" } },
            axisBorder: { show: false },
              crosshairs: {
                  show: true,
                  width: 20,
                stroke: { width: 0 },
                  fill: {
                      type: 'solid',
                      color: '#487FFF40',
                  }
              }
          }
    }),

    // Common API fetch function
    fetchData: async (type, period) => {
        try {
            const response = await fetch(`/aiwave/admin/api/dashboard/stats/?type=${type}&period=${period}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            if (data.error) throw new Error(data.error);
            return data;
        } catch (error) {
            throw error;
        }
    },

    // Common update function for stats elements
    updateStatsElement: (elementId, value, prefix = '', suffix = '') => {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = `${prefix}${value}${suffix}`;
        }
    },

    // Common trend update function
    updateTrendElement: (elementId, value, isPositive) => {
        const element = document.getElementById(elementId);
        if (!element) return;

        const trendClass = isPositive ? 
            'text-success-600 dark:text-success-400' : 
            'text-danger-600 dark:text-danger-400';
        
        element.className = `inline-flex items-center gap-1 ${trendClass}`;
        element.innerHTML = `
            <iconify-icon icon="${isPositive ? 'bxs:up-arrow' : 'bxs:down-arrow'}" class="text-xs"></iconify-icon>
            ${value}
        `;
    }
};

// Chart instances
const charts = {
    sales: null,
    bar: null,
    userOverview: null,
    generatedContent: null
};

// Sales Chart
function initSalesChart() {
    const chartElement = document.querySelector("#chart");
    if (!chartElement) return;

    if (charts.sales) charts.sales.destroy();

    const options = {
        ...chartUtils.getBaseChartOptions(),
        series: [{ name: "Sales", data: [] }],
        stroke: {
            curve: 'smooth',
            colors: ['#487FFF'],
            width: 3
        },
        markers: {
            size: 0,
            strokeWidth: 3,
            hover: { size: 8 }
        },
        tooltip: {
            enabled: true,
            x: { show: true },
            y: {
                formatter: value => "$" + parseFloat(value).toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })
            }
        },
        yaxis: {
            labels: {
                formatter: value => "$" + parseFloat(value).toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }),
                style: { fontSize: "14px" }
            }
        }
    };

    charts.sales = new ApexCharts(chartElement, options);
    charts.sales.render();
    updateSalesChart('monthly');
}

async function updateSalesChart(period = 'monthly') {
    if (!charts.sales) return;

    try {
        const data = await chartUtils.fetchData('sales', period);
              
              // Update chart data
        charts.sales.updateSeries([{
                  name: "Sales",
            data: data.sales_data || []
        }]);
        
        charts.sales.updateOptions({
            xaxis: { categories: data.labels || [] }
        });

        // Update stats
        const totalAmount = parseFloat(data.total_amount || 0).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        chartUtils.updateStatsElement('totalSalesAmount', totalAmount, '$');
        
        // Update trend
        const trendPercent = parseFloat(data.trend_percent || 0).toLocaleString('en-US', {
            minimumFractionDigits: 1,
            maximumFractionDigits: 1
        });
        chartUtils.updateTrendElement('salesTrend', trendPercent + '%', data.trend >= 0);
        
        // Update per period average
        const avgPerPeriod = data.sales_data && data.sales_data.length > 0 
            ? data.total_amount / data.sales_data.length 
            : 0;
        const periodText = period === 'today' ? 'Hour' : 'Day';
        const formattedAvg = parseFloat(avgPerPeriod).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        chartUtils.updateStatsElement('salesPerPeriod', 
            formattedAvg, 
            '+ $', 
            ` Per ${periodText}`);
    } catch (error) {
        // Set default values on error
        chartUtils.updateStatsElement('totalSalesAmount', '0.00', '$');
        chartUtils.updateTrendElement('salesTrend', '0%', true);
        chartUtils.updateStatsElement('salesPerPeriod', '0.00', '+ $', ' Per Day');
    }
}

// Bar Chart (Subscriber)
function initBarChart() {
    const options = {
        series: [{ name: "Subscribers", data: [] }],
      chart: {
          type: 'bar',
          height: 235,
            toolbar: { show: false }
      },
      plotOptions: {
          bar: {
            borderRadius: 6,
            horizontal: false,
            columnWidth: '52%',
                endingShape: 'rounded'
          }
      },
      fill: {
          type: 'gradient',
            colors: ['#dae5ff'],
          gradient: {
                shade: 'light',
                type: 'vertical',
                shadeIntensity: 0.5,
                gradientToColors: ['#dae5ff'],
                inverseColors: false,
                opacityFrom: 1,
                opacityTo: 1,
                stops: [0, 100]
            }
      },
      grid: {
          show: false,
          borderColor: '#D1D5DB',
            strokeDashArray: 4,
          position: 'back',
            padding: { top: -10, right: -10, bottom: -10, left: -10 }
        },
        xaxis: { type: 'category', categories: [] },
        yaxis: { show: false }
    };

    charts.bar = new ApexCharts(document.querySelector("#barChart"), options);
    charts.bar.render();
    updateSubscriberChart();
}

async function updateSubscriberChart(period = 'week') {
    if (!charts.bar) return;

    try {
        const data = await chartUtils.fetchData('subscriber', period);
        
        charts.bar.updateSeries([{
                  name: "Subscribers",
                  data: data.subscriber_data
              }]);
        
        charts.bar.updateOptions({
            xaxis: { categories: data.labels }
        });
    } catch (error) {
        // Handle error silently
    }
}

// User Overview Chart
  function initUserOverviewChart() {
      const chartElement = document.querySelector("#userOverviewDonutChart");
      if (!chartElement) return;

    if (charts.userOverview) charts.userOverview.destroy();

      const options = { 
        series: [0, 0, 0],
          colors: ['#FF9F29', '#487FFF', '#E4F1FF'],
          labels: ['Active', 'New', 'Total'],
          chart: {
              type: 'donut',    
              height: 270,
            sparkline: { enabled: true },
            margin: { top: 0, right: 0, bottom: 0, left: 0 },
            padding: { top: 0, right: 0, bottom: 0, left: 0 }
        },
        stroke: { width: 0 },
        dataLabels: { enabled: false },
        legend: { show: false },
          responsive: [{
              breakpoint: 480,
              options: {
                chart: { width: 200 },
                legend: { position: 'bottom' }
            }
        }]
    };

    charts.userOverview = new ApexCharts(chartElement, options);
    charts.userOverview.render();
      updateUserOverviewChart();
  }

async function updateUserOverviewChart(period = 'today') {
    if (!charts.userOverview) return;

    try {
        const data = await chartUtils.fetchData('user_overview', period);
        
        charts.userOverview.updateSeries([
                  data.active_users || 0,
                  data.new_users || 0,
                  data.total_users || 0
              ]);

        chartUtils.updateStatsElement('newUsersCount', data.new_users || 0);
        chartUtils.updateStatsElement('subscribedUsersCount', data.subscribed_users || 0);
    } catch (error) {
        charts.userOverview.updateSeries([0, 0, 0]);
    }
}

// Generated Content Chart
function initGeneratedContentChart() {
    const chartElement = document.querySelector("#generatedContentChart");
    if (!chartElement) return;

    if (charts.generatedContent) charts.generatedContent.destroy();

    const options = {
        ...chartUtils.getBaseChartOptions(300),
        series: [
            { name: "Sessions", data: [] },
            { name: "Messages", data: [] }
        ],
        stroke: {
            curve: 'smooth',
      colors: ['#487FFF', '#FF9F29'],
            width: 3
        },
        markers: {
            size: 0,
            strokeWidth: 3,
            hover: { size: 8 }
        },
        tooltip: {
            enabled: true,
            x: { show: true },
            y: { 
                formatter: value => value.toLocaleString('en-US', {
                    maximumFractionDigits: 0
                })
            }
        },
        yaxis: {
            labels: {
                formatter: value => value.toLocaleString('en-US', {
                    maximumFractionDigits: 0
                }),
                style: { fontSize: "14px" }
            },
            min: 0,
            forceNiceScale: true
        },
      legend: {
            position: 'top',
            horizontalAlign: 'center',
            offsetY: 20,
            markers: {
                width: 12,
                height: 12,
                radius: 6
            }
      },
      chart: {
            ...chartUtils.getBaseChartOptions(300).chart,
            toolbar: { show: false },
            zoom: { enabled: false },
            animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 800
            },
            offsetY: 40
      },
      grid: {
          show: true,
          borderColor: '#D1D5DB',
            strokeDashArray: 4,
          position: 'back',
            padding: { 
                top: 40,
                right: 0,
                bottom: 0,
                left: 0
            }
        }
    };

    charts.generatedContent = new ApexCharts(chartElement, options);
    charts.generatedContent.render();
    updateGeneratedContentData();
}

async function updateGeneratedContentData() {
    if (!charts.generatedContent) return;

    const period = document.getElementById('generatedContentPeriod')?.value || 'today';

    try {
        const data = await chartUtils.fetchData('generated_content', period);
        
        // Ensure data arrays are properly initialized and handle null/undefined values
        const sessionsData = Array.isArray(data.sessions_data) ? data.sessions_data.map(val => val || 0) : [];
        const messagesData = Array.isArray(data.messages_data) ? data.messages_data.map(val => val || 0) : [];
        const labels = Array.isArray(data.labels) ? data.labels : [];
        
        // Update chart data with proper data validation
        charts.generatedContent.updateSeries([
            { 
                name: "Sessions", 
                data: sessionsData
            },
            { 
                name: "Messages", 
                data: messagesData
            }
        ]);

        charts.generatedContent.updateOptions({
            xaxis: { 
                categories: labels,
                labels: {
                    style: { fontSize: "14px" }
                }
            }
        });

        // Update stats with proper formatting and validation
        const totalSessions = parseInt(data.total_sessions || 0);
        const totalMessages = parseInt(data.total_messages || 0);
        const periodTotalSessions = parseInt(data.period_total_sessions || 0);
        const periodTotalMessages = parseInt(data.period_total_messages || 0);

        // Use period totals if available, otherwise use today's totals
        const displaySessions = periodTotalSessions || totalSessions;
        const displayMessages = periodTotalMessages || totalMessages;
        
        chartUtils.updateStatsElement('totalSessionsCount', displaySessions.toLocaleString('en-US'));
        chartUtils.updateStatsElement('totalMessagesCount', displayMessages.toLocaleString('en-US'));
    } catch (error) {
        // Set default values on error
        charts.generatedContent.updateSeries([
            { name: "Sessions", data: [] },
            { name: "Messages", data: [] }
        ]);
        chartUtils.updateStatsElement('totalSessionsCount', '0');
        chartUtils.updateStatsElement('totalMessagesCount', '0');
    }
}

// Dashboard Stats
async function updateDashboardStats() {
    try {
        // Update Total Users
        chartUtils.updateStatsElement('dashboardTotalUsersCount', window.totalUsers || '0');
        chartUtils.updateTrendElement('totalUsersTrend', window.users30 || '0', parseFloat(window.usersTrend) >= 0);

        // Update Total Subscription
        chartUtils.updateStatsElement('totalSubscriptionCount', window.totalSubscriptions || '0');
        chartUtils.updateTrendElement('totalSubscriptionTrend', window.subscriptionTrendAbs || '0', parseFloat(window.subscriptionTrend) >= 0);

        // Update Total Free Users
        chartUtils.updateStatsElement('totalFreeUsersCount', window.totalFreeUsers || '0');
        chartUtils.updateTrendElement('totalFreeUsersTrend', window.freeUsersTrendAbs || '0', parseFloat(window.freeUsersTrend) >= 0);
    } catch (error) {
        // Handle error silently
    }
}

// Initialize all charts when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all charts
    initSalesChart();
    initBarChart();
    initUserOverviewChart();
    initGeneratedContentChart();
    
    // Initialize dashboard stats
    updateDashboardStats();

    // Set up event listeners for period changes
    const periodSelectors = {
        'salesPeriodSelect': updateSalesChart,
        'subscriberPeriod': updateSubscriberChart,
        'userOverviewPeriod': updateUserOverviewChart,
        'generatedContentPeriod': updateGeneratedContentData
    };

    Object.entries(periodSelectors).forEach(([id, updateFn]) => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', function() {
                updateFn(this.value);
            });
        }
    });
});