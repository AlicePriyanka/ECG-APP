// File generated for DefaultFirebaseOptions
import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, kIsWeb, TargetPlatform;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      throw UnsupportedError(
        'DefaultFirebaseOptions have not been configured for web',
      );
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        return ios;
      default:
        throw UnsupportedError(
          'DefaultFirebaseOptions are not supported for this platform.',
        );
    }
  }

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'AIzaSyABPersh6xVwrCql8vey7YGaTJbaGcR9k4',
    appId: '1:873893347572:android:c54535dc719e11ab775ea1',
    messagingSenderId: '873893347572',
    projectId: 'saveethacardioapp',
    storageBucket: 'saveethacardioapp.firebasestorage.app',
  );

  static const FirebaseOptions ios = FirebaseOptions(
    apiKey: 'AIzaSyADW1-RuM8ezH8iXPyaxQRzCQaoy4BPQ7k',
    appId: '1:873893347572:ios:f3d844de8abf5c72775ea1',
    messagingSenderId: '873893347572',
    projectId: 'saveethacardioapp',
    storageBucket: 'saveethacardioapp.firebasestorage.app',
    iosBundleId: 'com.simats.simatscardio',
  );
}
