from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from myapp.services.stocks_trained_models_service import StocksTrainedModelsService
from myapp.models import Stock, StocksPrediction
from myapp.repositories.stocks_trained_models_repository import StocksTrainedModelsRepository
from myapp.tasks import train_stock_model_async


@swagger_auto_schema(
    method='GET',
    operation_description="Get predictions for a given stock.",
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'predictions': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'timestamp': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Prediction date in ISO format."
                            ),
                            'predicted_value': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Predicted stock price."
                            )
                        }
                    )
                )
            }
        ),
        404: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Error message."
                )
            }
        )
    }
)
@api_view(['GET'])
def get_stock_predictions(request, stock_symbol):
    try:
        stock = Stock.objects.get(stock_symbol__iexact=stock_symbol)
    except Stock.DoesNotExist:
        return Response({"error": "Stock not found"}, status=status.HTTP_404_NOT_FOUND)

    predictions = StocksPrediction.objects.filter(stock=stock).order_by('prediction_date')
    data = [{
        "timestamp": p.prediction_date.isoformat(),
        "predicted_value": str(p.predicted_value)
    } for p in predictions]
    return Response({"predictions": data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='POST',
    operation_description="Start asynchronous training of a stock model",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'stock_symbol': openapi.Schema(type=openapi.TYPE_STRING, description="Symbol of the stock to train on."),
            'param_grid': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                default={
                    'rnn_type': ['LSTM'],
                    'n_layers': [1],
                    'units': [50],
                    'activation': ['relu'],
                    'optimizer': ['adam'],
                    'batch_size': [32],
                    'epochs': [50]
                },
                description="Grid of parameters for model training."
            ),
            'sequence_length': openapi.Schema(type=openapi.TYPE_INTEGER, default=14,
                                              description="Length of input sequences."),
            'dataset_time': openapi.Schema(type=openapi.TYPE_INTEGER, default=6,
                                           description="Number of years of data to use."),
            'prediction_steps': openapi.Schema(type=openapi.TYPE_INTEGER, default=90,
                                               description="Number of days to predict ahead."),
            'short_term_lag': openapi.Schema(type=openapi.TYPE_INTEGER, default=7,
                                             description="Short-term lag in days."),
            'long_term_lag': openapi.Schema(type=openapi.TYPE_INTEGER, default=30,
                                            description="Long-term lag in days."),
            'scaling_method': openapi.Schema(type=openapi.TYPE_STRING, default='standard',
                                             description="Scaling method for features."),
            'output_directory': openapi.Schema(type=openapi.TYPE_STRING, default='forecasting_outputs',
                                               description="Directory to store output files."),
        },
        required=['stock_symbol']
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="Success message."),
                "task_id": openapi.Schema(type=openapi.TYPE_STRING, description="ID of the asynchronous task.")
            }
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message.")
            }
        )
    }
)
@api_view(['POST'])
def start_async_stock_training(request):
    stock_symbol = request.data.get('stock_symbol')
    if not stock_symbol:
        return Response({"error": "Missing stock_symbol"}, status=status.HTTP_400_BAD_REQUEST)

    param_grid = request.data.get('param_grid', {
        'rnn_type': ['LSTM'],
        'n_layers': [1],
        'units': [50],
        'activation': ['relu'],
        'optimizer': ['adam'],
        'batch_size': [32],
        'epochs': [50]
    })

    sequence_length = int(request.data.get('sequence_length', 14))
    dataset_time = int(request.data.get('dataset_time', 6))
    prediction_steps = int(request.data.get('prediction_steps', 90))
    short_term_lag = int(request.data.get('short_term_lag', 7))
    long_term_lag = int(request.data.get('long_term_lag', 30))
    scaling_method = request.data.get('scaling_method', 'standard')
    output_directory = request.data.get('output_directory', 'forecasting_outputs')

    task = train_stock_model_async.delay(
        stock_symbol,
        param_grid,
        sequence_length,
        dataset_time,
        prediction_steps,
        short_term_lag,
        long_term_lag,
        scaling_method,
        output_directory
    )

    return Response({"message": "Training task started", "task_id": task.id}, status=status.HTTP_200_OK)