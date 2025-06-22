package com.spottenn.luxoai

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.spottenn.luxoai.ui.theme.LuxoAITheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        // Log API keys from BuildConfig for verification
        // Important: In a real app, avoid logging actual keys.
        // This is for setup verification only.
        // Consider using BuildConfig.DEBUG to only log in debug builds.
        Log.d("MainActivitySecrets", "OpenAI Key: ${BuildConfig.OPENAI_API_KEY}")
        Log.d("MainActivitySecrets", "Anthropic Key: ${BuildConfig.ANTHROPIC_API_KEY}")
        Log.d("MainActivitySecrets", "Replicate Token: ${BuildConfig.REPLICATE_API_TOKEN}")

        setContent {
            LuxoAITheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    Greeting(
                        name = "Android",
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }
    }
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello $name!",
        modifier = modifier
    )
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    LuxoAITheme {
        Greeting("Android")
    }
}